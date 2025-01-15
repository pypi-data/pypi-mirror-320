import re
from collections.abc import Iterable
from xml.dom.minidom import parseString

import dicttoxml
import xmltodict


class XMLUtils:
    @staticmethod
    def dict_to_xml(data: dict | list, format: bool = False, **kwargs) -> str:
        result = dicttoxml.dicttoxml(data, return_bytes=False, **kwargs)
        if not isinstance(result, str):
            raise ValueError("Failed to convert dict to XML")
        if format:
            result = parseString(result).toprettyxml()
        return result

    @staticmethod
    def add_cdata_to_function_body(xml_string):
        pattern = r"(<function_body>)(.*?)(</function_body>)"
        replacement = r"\1<![CDATA[\2]]>\3"
        updated_xml_string = re.sub(pattern, replacement, xml_string, flags=re.DOTALL)
        return updated_xml_string

    @staticmethod
    def add_cdata_to_tags(xml_string: str, tags: Iterable[str]) -> str:
        patterns = [rf"(<{tag}>)(.*?)(</{tag}>)" for tag in tags]
        updated_xml_string = xml_string

        for pattern in patterns:
            replacement = r"\1<![CDATA[\2]]>\3"
            updated_xml_string = re.sub(pattern, replacement, updated_xml_string, flags=re.DOTALL)

        return updated_xml_string

    @staticmethod
    def xml_to_dict(xml_string: str, **kwargs) -> dict:
        return xmltodict.parse(XMLUtils.add_cdata_to_tags(xml_string, ["function_body", "reasoning"]), **kwargs)

    @staticmethod
    def strip_after_tag(xml_string, tag):
        pattern = re.compile(f"<{tag}.*?>.*", re.DOTALL)
        match = pattern.search(xml_string)
        if match:
            return xml_string[: match.start()]
        else:
            return xml_string

    @staticmethod
    def strip_tag(xml_string: str, tag: str):
        pattern = re.compile(f"<{tag}>.*?</{tag}>", re.DOTALL)
        return pattern.sub("", xml_string).strip()

    @staticmethod
    def strip_all_tags(xml_string: str):
        pattern = re.compile(r"<[^>]*>")
        return pattern.sub("", xml_string).strip()

    @staticmethod
    def extract_elements(xml_string: str, tag: str, keep_tag: bool = False) -> list[str]:
        pattern = re.compile(f"<{tag}.*?</{tag}>", re.DOTALL)
        matches = pattern.findall(xml_string)
        if keep_tag:
            return matches
        else:
            return [match.strip(f"<{tag}>").strip(f"</{tag}>") for match in matches]
