import re
import tarfile  # type: ignore
from functools import reduce
from pathlib import Path
from typing import Dict, Any, List, Set, Pattern

import lxml.etree  # type: ignore
from rest_framework.exceptions import ParseError, \
    ValidationError  # type: ignore

from nextcloudappstore.api.v1.release import ReleaseConfig
from nextcloudappstore.core.versioning import pad_max_version, \
    pad_min_version, raw_version


class MaxFileSizeExceeded(ValidationError):
    pass


class InvalidAppMetadataXmlException(ValidationError):
    pass


class UnsupportedAppArchiveException(ValidationError):
    pass


class InvalidAppPackageStructureException(ValidationError):
    pass


class ForbiddenLinkException(InvalidAppPackageStructureException):
    pass


class XMLSyntaxError(ParseError):
    pass


class BlacklistedMemberException(ValidationError):
    pass


class AppMetaData:
    def __init__(self, info_xml: str, database_xml: str, app_id: str,
                 changelog: Dict[str, str]) -> None:
        self.changelog = changelog
        self.app_id = app_id
        self.database_xml = database_xml
        self.info_xml = info_xml


class GunZipAppMetadataExtractor:
    def __init__(self, config: ReleaseConfig) -> None:
        """
        :argument config the config
        """
        self.config = config
        self.app_folder_regex = re.compile(r'^[a-z]+[a-z0-9_]*(?:/.*)*$')

    def extract_app_metadata(self, archive_path: str) -> AppMetaData:
        """
        Extracts the info.xml from an tar.gz archive
        :argument archive_path: the path to the tar.gz archive
        :raises InvalidAppPackageStructureException: if the first level folder
        does not equal the app_id or no info.xml file could be found in the
        appinfo folder
        :raises: UnsupportedAppArchiveException if it's not an archive
        :return: the info.xml, database.xml, the app id and the changelog as
        string
        """
        if not tarfile.is_tarfile(archive_path):  # type: ignore
            """
            Previously the message revealed full path to the archive which is
            unwanted. To mitigate the issue we now get only the filename
            and include that in the error message
            """
            msg = '%s is not a valid tar.gz archive ' % Path(archive_path).name
            raise UnsupportedAppArchiveException(msg)

        try:
            with tarfile.open(archive_path, 'r:gz') as tar:  # type: ignore
                result = self._parse_archive(tar)
            return result
        # for some reason there are still various errors possible although we
        # checked for issues with tarfile.is_tarfile
        except tarfile.ReadError as e:
            raise UnsupportedAppArchiveException(str(e))

    def _parse_archive(self, tar: Any) -> AppMetaData:
        app_id = find_app_id(tar, self.app_folder_regex)
        info = get_contents('%s/appinfo/info.xml' % app_id, tar,
                            self.config.max_file_size)
        database = get_contents('%s/appinfo/database.xml' % app_id, tar,
                                self.config.max_file_size, '')
        changelog = {
            'en': get_contents(
                '%s/CHANGELOG.md' % app_id, tar, self.config.max_file_size, ''
            )
        }  # type: Dict[str, str]

        for code, _ in self.config.languages:
            trans_changelog = get_contents(
                '%s/CHANGELOG.%s.md' % (app_id, code), tar,
                self.config.max_file_size, '')
            if trans_changelog:
                changelog[code] = trans_changelog

        # validate invalid members here due to possible massive amount of
        # files (e.g. .git directories)
        test_blacklisted_members(tar, self.config.member_blacklist)

        return AppMetaData(info, database, app_id, changelog)


def get_contents(path: str, tar: Any, max_file_size: int,
                 default: Any = None) -> str:
    """
    Reads the contents of a file
    :param path: the path to the target file
    :param tar: the tar file
    :param max_file_size: maximum allowed file size in bytes
    :param default: default if file is not found in the directory
    :raises InvalidAppPackageStructureException: if the path does not exist
     and the default is None
    :return: the contents of the file if found or the default
    """
    member = find_member(tar, path)
    if member is None:
        if default is not None:
            return default
        msg = 'Path %s does not exist in package' % path
        raise InvalidAppPackageStructureException(msg)
    return stream_read_utf8(tar, member, max_file_size)


def find_app_id(tar: Any, app_folder_regex: Pattern) -> str:
    """
    Finds and returns the app id by looking at the first level folder
    :raises InvalidAppPackageStructureException: if there is no valid or
     to many app folders
    :param tar: the archive
    :return: the app id
    """
    folders = find_app_folders(tar, app_folder_regex)
    if len(folders) > 1:
        msg = 'More than one possible app folder found'
        raise InvalidAppPackageStructureException(msg)
    elif len(folders) == 0:
        msg = 'No possible app folder found. App folder must contain ' \
              'only lowercase ASCII characters or underscores'
        raise InvalidAppPackageStructureException(msg)
    return folders.pop()


def find_app_folders(tar: Any, app_folder_regex: Pattern) -> Set[str]:
    return {
        folder.split('/')[0]
        for folder in tar.getnames()
        if re.match(app_folder_regex, folder)
    }


def test_blacklisted_members(tar, blacklist):
    """
    :param tar: the tar file
    :raises: BlacklistedMemberException
    :return:
    """
    names = []
    for n in tar.getnames():
        try:
            if tar.getmember(n).isdir():
                names.append(n)
        except KeyError:
            pass

    for name in names:
        for error, regex in blacklist.items():
            regex = re.compile(regex)
            if regex.search(name):
                msg = 'Blacklist rule "%s": Directory %s is not ' \
                      'allowed to be present in the app ' \
                      'archive' % (error, name)
                raise BlacklistedMemberException(msg)


def element_to_dict(element: Any) -> Dict:
    type = element.get('type')
    key = element.tag.replace('-', '_')
    if type == 'int' and element.text is not None:
        return {key: int(element.text)}
    elif type == 'list':
        return {key: list(map(element_to_dict, element.iterchildren()))}
    elif type == 'min-version':
        return {
            key: pad_min_version(element.text),
            'raw_%s' % key: raw_version(element.text)
        }
    elif type == 'max-version':
        return {
            key: pad_max_version(element.text),
            'raw_%s' % key: raw_version(element.text)
        }
    elif len(list(element)) > 0:
        contents = {}
        for child in element.iterchildren():
            contents.update(element_to_dict(child))
        return {key: contents}
    else:
        return {key: element.text}


def create_safe_xml_parser() -> lxml.etree.XMLParser:
    return lxml.etree.XMLParser(  # type: ignore
        resolve_entities=False, no_network=True,  # type: ignore
        remove_comments=True, load_dtd=False,  # type: ignore
        remove_blank_text=True, dtd_validation=False  # type: ignore
    )  # type: ignore


def parse_app_metadata(xml: str, schema: str, pre_xslt: str,
                       xslt: str) -> Dict:
    """
    Parses, validates and maps the xml onto a dict
    :argument xml the info.xml string to parse
    :argument schema the schema xml as string
    :argument pre_xslt xslt which is run before validation to ensure that
    everything is in the correct order and that unknown elements are excluded
    :argument xslt the xslt to transform it to a matching structure
    :raises InvalidAppMetadataXmlException if the schema does not validate
    :return the parsed xml as dict
    """
    parser = create_safe_xml_parser()
    try:
        doc = lxml.etree.fromstring(bytes(xml, encoding='utf-8'), parser)
    except lxml.etree.XMLSyntaxError as e:
        msg = 'info.xml contains malformed xml: %s' % e
        raise XMLSyntaxError(msg)
    for _ in doc.iter(lxml.etree.Entity):  # type: ignore
        raise InvalidAppMetadataXmlException('Must not contain entities')
    pre_transform = lxml.etree.XSLT(lxml.etree.XML(pre_xslt))  # type: ignore
    pre_transformed_doc = pre_transform(doc)
    schema_doc = lxml.etree.fromstring(bytes(schema, encoding='utf-8'), parser)
    schema = lxml.etree.XMLSchema(schema_doc)  # type: ignore
    try:
        schema.assertValid(pre_transformed_doc)  # type: ignore
    except lxml.etree.DocumentInvalid as e:
        msg = 'info.xml did not validate: %s' % e
        raise InvalidAppMetadataXmlException(msg)
    transform = lxml.etree.XSLT(lxml.etree.XML(xslt))  # type: ignore
    transformed_doc = transform(pre_transformed_doc)  # type: ignore
    mapped = element_to_dict(transformed_doc.getroot())  # type: ignore
    validate_english_present(mapped)
    fix_partial_translations(mapped)
    return mapped


def validate_database(xml: str, schema: str, pre_xslt: str) -> None:
    """
    Validates a database.xml
    :argument xml the database.xml string to parse
    :argument schema the schema xml as string
    :argument pre_xslt xslt which is run before validation to ensure that
    everything is in the correct order and that unknown elements are excluded
    :raises InvalidAppMetadataXmlException if the schema does not validate
    """
    parser = create_safe_xml_parser()
    try:
        doc = lxml.etree.fromstring(bytes(xml, encoding='utf-8'), parser)
    except lxml.etree.XMLSyntaxError as e:
        msg = 'database.xml contains malformed xml: %s' % e
        raise XMLSyntaxError(msg)
    for _ in doc.iter(lxml.etree.Entity):  # type: ignore
        raise InvalidAppMetadataXmlException('Must not contain entities')
    pre_transform = lxml.etree.XSLT(lxml.etree.XML(pre_xslt))  # type: ignore
    pre_transformed_doc = pre_transform(doc)
    schema_doc = lxml.etree.fromstring(bytes(schema, encoding='utf-8'), parser)
    schema = lxml.etree.XMLSchema(schema_doc)  # type: ignore
    try:
        schema.assertValid(pre_transformed_doc)  # type: ignore
    except lxml.etree.DocumentInvalid as e:
        msg = 'database.xml did not validate: %s' % e
        raise InvalidAppMetadataXmlException(msg)


def validate_english_present(info: Dict) -> None:
    """
    Validates that name, summary and description are present in english
    :param info: the parsed xml
    :raises: InvalidAppMetadataXmlException if at least one of the required
     fields is not present in english
    """
    app = info['app']
    translated_fields = ['name', 'summary', 'description']
    for field in translated_fields:
        if 'en' not in app[field]:
            msg = 'At least one element "%s" with lang "en" required' % field
            raise InvalidAppMetadataXmlException(msg)


def fix_partial_translations(info: Dict) -> None:
    """
    Collects translations and adds english fallbacks
    :param info: the parsed info.xml
    :return: None
    """
    app = info['app']
    trans_fields = ['name', 'summary', 'description']
    fields = [field for field in trans_fields if field in app]
    codes = set()  # type: Set[str]
    for field in fields:
        codes |= set(app[field].keys())
    for field in fields:
        absent_codes = [code for code in codes if code not in app[field]]
        for code in absent_codes:
            app[field][code] = app[field]['en']


def parse_changelog(changelog: str, version: str,
                    is_nightly: bool = False) -> str:
    """
    Parses and finds the changelog for the current version. Follows the "Keep
    a changelog" format.
    :param changelog: the full changelog
    :param version: the version to look for
    :param is_nightly: if the version is a nightly
    :return: the parsed changelog
    """
    if is_nightly or '-' in version:
        version = 'Unreleased'
    changelog = changelog.strip()
    regex = re.compile(r'^## (?:\[)?(?:v)?(\d+\.\d+(\.\d+)?)')
    unstable_regex = re.compile(r'^## \[Unreleased\]')
    result = {}  # type: Dict[str, List[str]]
    curr_version = ''
    empty_list = []  # type: List[str]
    for line in changelog.splitlines():
        search = re.search(regex, line)
        unstable_search = re.match(unstable_regex, line)
        if search:
            curr_version = search.group(1)
        elif unstable_search:
            curr_version = 'Unreleased'
        else:
            result[curr_version] = result.get(curr_version, empty_list) + [
                line]
    return '\n'.join(result.get(version, empty_list)).strip()


def stream_read_utf8(tarfile: Any, path: str, max_size: int) -> str:
    """
    Same as stream_read_file but converts the result to uft8
    :param tarfile:
    :param path: path to file to read in tar file
    :param max_size: maximum allowed size
    :raises MaxFileSizeExceeded: if the maximum size was reached
    :return: the file as text
    """
    return stream_read_file(tarfile, path, max_size).decode('utf-8')


def stream_read_file(tarfile: Any, path: str, max_size: int) -> bytes:
    """
    Instead of reading everything in one go which is vulnerable to
    zip bombs, stream and accumulate the bytes
    :param tarfile:
    :param path: path to file to read in tar file
    :param max_size: maximum allowed size
    :raises MaxFileSizeExceeded: if the maximum size was reached
    :return: the file as binary
    """
    file = tarfile.extractfile(path)

    size = 0
    result = b''
    while True:
        size += 1024
        if size > max_size:
            msg = 'file %s was bigger than allowed %i bytes' % (path, max_size)
            raise MaxFileSizeExceeded(msg)
        chunk = file.read(1024)
        if not chunk:
            break
        result += chunk
    return result


def find_member(tar: Any, path: str) -> Any:
    """
    Validates that the path to the target member and the member itself
    is not a symlink to prevent arbitrary file inclusion, then returns
    the member in question
    :param tar: the tar file
    :param path: the target member to check
    :raises InvalidAppPackageStructureException: if links are found
    :return: the member if found, otherwise None
    """

    def build_paths(prev: List[str], curr: str) -> List[str]:
        """Builds a List of paths to the target from a list of path
        fragments, e.g.: ['a', 'a/path'], 'tofile' is being turned into
        ['a', 'a/path', 'a/path/tofile']
        :param prev: the previous result list
        :param curr: the current result
        :return: the previous list with the new result which was
        constructed from the last element and the current element
        """
        if prev:
            return prev + ['%s/%s' % (prev[-1], curr)]
        else:
            return [curr]

    def check_member(path: str) -> Any:
        """Tries to get a member for a path or None if not found"""
        try:
            return tar.getmember(path)
        except KeyError:
            return None

    default = []  # type: List[str]
    member_paths = reduce(build_paths, path.split('/'), default)
    checked_members = [check_member(m) for m in member_paths]

    for member in filter(lambda m: m is not None, checked_members):
        if member.issym() or member.islnk():
            msg = 'Symlinks and hard links can not be used for %s' % member
            raise ForbiddenLinkException(msg)
    return check_member(path)
