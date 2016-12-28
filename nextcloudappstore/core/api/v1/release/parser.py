import re
import tarfile  # type: ignore
from functools import reduce

import lxml.etree  # type: ignore
from typing import Dict, Any, Tuple, List, Set

from semantic_version import Version

from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.versioning import pad_max_version, \
    pad_min_version, raw_version
from rest_framework.exceptions import ParseError, \
    ValidationError  # type: ignore


class MaxSizeAppMetadataXmlException(ValidationError):
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


Metadata = Tuple[str, str, Dict[str, str]]


class GunZipAppMetadataExtractor:
    def __init__(self, config: ReleaseConfig) -> None:
        """
        :argument config the config
        """
        self.config = config
        self.app_folder_regex = re.compile(r'^[a-z]+[a-z0-9_]*(?:/.*)*$')

    def extract_app_metadata(self, archive_path: str) -> Metadata:
        """
        Extracts the info.xml from an tar.gz archive
        :argument archive_path: the path to the tar.gz archive
        :raises InvalidAppPackageStructureException: if the first level folder
        does not equal the app_id or no info.xml file could be found in the
        appinfo folder
        :return: the info.xml, the app id and the changelog as string
        """
        if not tarfile.is_tarfile(archive_path):  # type: ignore
            msg = '%s is not a valid tar.gz archive ' % archive_path
            raise UnsupportedAppArchiveException(msg)

        with tarfile.open(archive_path, 'r:gz') as tar:  # type: ignore
            result = self._parse_archive(tar)
        return result

    def _parse_archive(self, tar: Any) -> Metadata:
        app_id = self._find_app_id(tar)
        info = self._get_contents('%s/appinfo/info.xml' % app_id, tar)
        changelog = {}  # type: Dict[str, str]
        changelog['en'] = self._get_contents('%s/CHANGELOG.md' % app_id, tar,
                                             '')
        for code, _ in self.config.languages:
            trans_changelog = self._get_contents(
                '%s/CHANGELOG.%s.md' % (app_id, code), tar, ''
            )
            if trans_changelog:
                changelog[code] = trans_changelog

        return info, app_id, changelog

    def _get_contents(self, path: str, tar: Any, default: Any = None) -> str:
        """
        Reads the contents of a file
        :param path: the path to the target file
        :param tar: the tar file
        :param default: default if file is not found in the directory
        :raises InvalidAppPackageStructureException: if the path does not exist
         and the default is None
        :return: the contents of the file if found or the default
        """
        member = self._find_member(path, tar)
        if member is None:
            if default is None:
                msg = 'Path %s does not exist in package' % path
                raise InvalidAppPackageStructureException(msg)
            else:
                return default
        file = tar.extractfile(member)
        return self._stream_read_file(file, self.config.max_info_size)

    def _find_member(self, path: str, tar: Any) -> Any:
        """
        Validates that the path to the target member and the member itself
        is not a symlink to prevent abitrary file inclusion, then returns
        the member in question
        :param info_member: the target member to check
        :param tar: tge tar file
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
            if len(prev) > 0:
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
                msg = 'Symlinks and hard links can not be used for %s' % \
                      member
                raise ForbiddenLinkException(msg)
        return check_member(path)

    def _find_app_id(self, tar: Any) -> str:
        """
        Finds and returns the app id by looking at the first level folder
        :raises InvalidAppPackageStructureException: if there is no valid or
         to many app folders
        :param tar: the archive
        :return: the app id
        """
        folders = self._find_app_folders(tar.getnames())
        if len(folders) > 1:
            msg = 'More than one possible app folder found'
            raise InvalidAppPackageStructureException(msg)
        elif len(folders) == 0:
            msg = 'No possible app folder found. App folder must contain ' \
                  'only lowercase ASCII characters or underscores'
            raise InvalidAppPackageStructureException(msg)
        return folders.pop()

    def _find_app_folders(self, members: List[str]) -> Set[str]:
        """
        Find a set of valid app folders
        :param members: a list of tar members
        :return: a set of valid app folders
        """
        regex = self.app_folder_regex
        matching_members = filter(lambda f: re.match(regex, f), members)
        folders = map(lambda m: m.split('/')[0], matching_members)
        return set(folders)

    def _stream_read_file(self, info_file: Any, max_info_size: int) -> str:
        """
        Instead of reading everything in one go which is vulnerable to
        zip bombs, stream and accumulate the bytes
        :argument info_file: buffered io reader
        :argument max_info_size: maximum file size in bytes
        :raises MaxSizeAppMetadataXmlException if the maximum size was reached
        :return: the parsed info.xml
        """
        # FIXME: If someone finds a less ugly version, please feel free to
        #        improve it
        size = 0
        result = b''
        while True:
            size += 1024
            if size > max_info_size:
                msg = 'info.xml was bigger than allowed %i bytes' % \
                      max_info_size
                raise MaxSizeAppMetadataXmlException(msg)

            chunk = info_file.read(1024)
            if not chunk:
                break
            result += chunk

        return result.decode('utf-8')


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
    parser = lxml.etree.XMLParser(  # type: ignore
        resolve_entities=False, no_network=True,  # type: ignore
        remove_comments=True, load_dtd=False,  # type: ignore
        remove_blank_text=True, dtd_validation=False  # type: ignore
    )  # type: ignore
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
    validate_pre_11(mapped, doc)
    fix_partial_translations(mapped)
    return mapped


def validate_pre_11(info: Dict, doc: Any) -> None:
    """
    Apps before 11 need to provide an owncloud min-version tag to run
    :param info: the transformed and parsed info xml
    :param doc: the original xml document
    :raises: InvalidAppMetadataXmlException if no owncloud min-version is
    present for apps with min-version 9 or 10
    """
    min_version = Version(info['app']['release']['platform_min_version'])

    test_xpath = 'dependencies/owncloud'
    if min_version < Version('11.0.0') and len(doc.xpath(test_xpath)) == 0:
        msg = '<owncloud> tag is required for apps that run on Nextcloud 9 ' \
              'and 10'
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
    regex = re.compile(r'^## (?:\[)?(\d+\.\d+\.\d+)')
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
