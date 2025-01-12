from lxml.html import fromstring

from .utils import get_string_matching_xpath


class StructuredPathGenerator:
    def __init__(self, html_content):
        self.lxml = fromstring(html_content)

    def __match_str(self, target: str) -> str:
        matches = self.lxml.xpath(get_string_matching_xpath(target))
        if not matches:
            return None
        return self.lxml.getroottree().getpath(matches[0])

    def __match_value(
        self, target: str | dict[str, any] | list[str | dict[str, any]]
    ) -> str:
        if isinstance(target, str):
            return self.__match_str(target)
        elif isinstance(target, dict):
            return self.__match_dict(target)
        elif isinstance(target, list):
            return [self.__match_value(value) for value in target]
        else:
            return None

    def __match_dict(self, target: dict[str, any]):
        return {key: self.__match_value(value) for key, value in target.items()}

    def match(self, target: dict[str, any]):
        return self.__match_dict(target)


class StructuredPathScraper:
    def __init__(self, html_content):
        self.lxml = fromstring(html_content)

    def __fetch_xpath(self, xpath: str) -> str:
        matches = self.lxml.xpath(f"({xpath})[1]")
        if not matches:
            return None
        return matches[0].text_content()

    def __fetch_value(
        self, target: str | dict[str, any] | list[str | dict[str, any]]
    ) -> str:
        if isinstance(target, str):
            return self.__fetch_xpath(target)
        elif isinstance(target, dict):
            return self.__fetch_dict(target)
        elif isinstance(target, list):
            return [self.__fetch_value(value) for value in target]
        else:
            return None

    def __fetch_dict(self, target: dict[str, any]):
        return {key: self.__fetch_value(value) for key, value in target.items()}

    def fetch(self, target: dict[str, any]):
        return self.__fetch_dict(target)
