import re
import tarfile  # type: ignore
import lxml.etree  # type: ignore
from typing import Dict, Any, Tuple, List, Set

from nextcloudappstore.core.api.v1.release import ReleaseConfig
from nextcloudappstore.core.versioning import pad_max_version, pad_min_version
from rest_framework.exceptions import APIException  # type: ignore


class MaxSizeAppMetadataXmlException(APIException):
    pass


class InvalidAppMetadataXmlException(APIException):
    pass


class UnsupportedAppArchiveException(APIException):
    pass


class InvalidAppPackageStructureException(APIException):
    pass


class XMLSyntaxError(APIException):
    pass


class GunZipAppMetadataExtractor:
    def __init__(self, config: ReleaseConfig) -> None:
        """
        :argument config the config
        """
        self.config = config
        self.app_folder_regex = re.compile(r'^[a-z]+[a-z_]*(?:/.*)*$')

    def extract_app_metadata(self, archive_path: str) -> Tuple[str, str]:
        """
        Extracts the info.xml from an tar.gz archive
        :argument archive_path the path to the tar.gz archive
        :raises InvalidAppPackageStructureException if the first level folder
        does not equal the app_id or no info.xml file could be found in the
        appinfo folder
        :return the info.xml as string
        """
        if not tarfile.is_tarfile(archive_path):
            msg = '%s is not a valid tar.gz archive ' % archive_path
            raise UnsupportedAppArchiveException(msg)

        with tarfile.open(archive_path, 'r:gz') as tar:
            result = self._parse_archive(tar)
        return result

    def _parse_archive(self, tar: Any) -> Tuple[str, str]:
        folders = self._find_app_folders(tar.getnames())
        if len(folders) > 1:
            msg = 'More than one possible app folder found'
            raise InvalidAppPackageStructureException(msg)
        elif len(folders) == 0:
            msg = 'No possible app folder found. App folder must contain ' \
                  'only lowercase ASCII characters or underscores'
            raise InvalidAppPackageStructureException(msg)

        app_id = folders.pop()
        info_path = '%s/appinfo/info.xml' % app_id
        try:
            info_member = tar.getmember(info_path)
            possible_links = [info_member]
            # its complicated, sometimes there are single members, sometimes
            # there aren't
            try:
                possible_links.append(tar.getmember(app_id))
            except KeyError:
                pass
            try:
                possible_links.append(tar.getmember('%s/appinfo' % app_id))
            except KeyError:
                pass

            for possible_link in possible_links:
                if possible_link.issym() or possible_link.islnk():
                    msg = 'Symlinks and hard links can not be used for %s' % \
                          possible_link
                    raise InvalidAppPackageStructureException(msg)
            info_file = tar.extractfile(info_member)
            contents = self._stream_read_file(info_file,
                                              self.config.max_info_size)
            return contents, app_id
        except KeyError:
            msg = 'Could not find %s file inside the archive' % info_path
            raise InvalidAppPackageStructureException(msg)

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

    def _find_app_folders(self, members: List[str]) -> Set[str]:
        regex = self.app_folder_regex
        matching_members = filter(lambda f: re.match(regex, f), members)
        folders = map(lambda m: m.split('/')[0], matching_members)
        return set(folders)


def element_to_dict(element: Any) -> Dict:
    type = element.get('type')
    key = element.tag.replace('-', '_')
    if type == 'int':
        return {key: int(element.text)}
    elif type == 'list':
        return {key: list(map(element_to_dict, element.iterchildren()))}
    elif type == 'min-version':
        return {key: pad_min_version(element.text)}
    elif type == 'max-version':
        return {key: pad_max_version(element.text)}
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
    parser = lxml.etree.XMLParser(resolve_entities=False, no_network=True,
                                  remove_comments=True, load_dtd=False,
                                  remove_blank_text=True, dtd_validation=False
                                  )
    try:
        doc = lxml.etree.fromstring(bytes(xml, encoding='utf-8'), parser)
    except lxml.etree.XMLSyntaxError as e:
        msg = 'info.xml contains malformed xml: %s' % e
        raise XMLSyntaxError(msg)
    for _ in doc.iter(lxml.etree.Entity):
        raise InvalidAppMetadataXmlException('Must not contain entities')
    pre_transform = lxml.etree.XSLT(lxml.etree.XML(pre_xslt))
    pre_transformed_doc = pre_transform(doc)
    schema_doc = lxml.etree.fromstring(bytes(schema, encoding='utf-8'), parser)
    schema = lxml.etree.XMLSchema(schema_doc)
    try:
        schema.assertValid(pre_transformed_doc)  # type: ignore
    except lxml.etree.DocumentInvalid as e:
        msg = 'info.xml did not validate: %s' % e
        raise InvalidAppMetadataXmlException(msg)
    transform = lxml.etree.XSLT(lxml.etree.XML(xslt))
    transformed_doc = transform(pre_transformed_doc)
    mapped = element_to_dict(transformed_doc.getroot())
    return mapped
