from enum import Enum
import itertools
from typing import Union

try:
    import bs4
except ImportError:
    raise RuntimeError("Library `BeautifulSoup4` is required to use `apptk.html`.")


class Selector:
    class PathType(Enum):
        CSS = "css"
        XPATH = "xpath"

    path_type: PathType
    paths: list[str] = None
    attribute: str = None
    strip_trailing_whitespace: bool = True
    strip_leading_whitespace: bool = True

    def __init__(
        self,
        path: Union[str, list[str]],
        path_type: PathType = PathType.CSS,
        attribute: str = None,
        strip_trailing_whitespace: bool = True,
        strip_leading_whitespace: bool = True,
    ):
        self.paths = [path] if isinstance(path, str) else path
        self.path_type = path_type
        self.attribute = attribute
        self.strip_leading_whitespace = strip_leading_whitespace
        self.strip_trailing_whitespace = strip_trailing_whitespace

    def get_attribute(self, element: bs4.element.Tag) -> str:
        """
        Extract the defined attribute's value from the passed in element.

        Extract the value of the attribute set by self.attribute from element. If self.attribute is None, then we just
        convert the body of element to text and return that.

        The result is stripped of leading/trailing whitespace depending on the values of self.strip_leading_whitespace
        and self.strip_trailing_whitespace, respectively.

        :param element: The element
        :return: The value of the attribute or the text of the element.
        """
        result = element.get(self.attribute) if self.attribute else element.text
        if self.strip_leading_whitespace:
            result = result.lstrip()
        if self.strip_trailing_whitespace:
            result = result.rstrip()
        return result

    def parse(self, html: bs4.element.Tag, use_attribute: bool = True) -> list[Union[str, bs4.element.Tag]]:
        return [
            self.get_attribute(element) if use_attribute else element
            for element in itertools.chain.from_iterable(html.select(path) for path in self.paths)
        ]

    def parse_one(self, html: bs4.element.Tag, use_attribute: bool = True):
        for path in self.paths:
            element = html.select_one(path)
            if element:
                return self.get_attribute(element) if use_attribute else element
