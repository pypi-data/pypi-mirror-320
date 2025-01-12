import json
from dataclasses import dataclass

import pytest

from structuredscraper import StructuredPathGenerator, StructuredPathScraper


@dataclass
class TestCase:
    __test__ = False
    html: str
    targets: dict[str, any]


@pytest.mark.parametrize(
    ("html", "targets"),
    [
        pytest.param(
            "<html><body><h1>test</h1></body></html>",
            json.loads(
                """{
                    "str": "test"
                }"""
            ),
            id="extract_single_string",
        ),
        pytest.param(
            "<html><body><h1>Hello</h1><div>World</div></body></html>",
            json.loads(
                """{
                    "h1_val": "Hello",
                    "div_val": "World"
                }"""
            ),
            id="extract_multiple_strings",
        ),
        pytest.param(
            "<html><body><h1>Hello</h1><h1>World</h1></body></html>",
            json.loads(
                """{
                    "h1_vals": [
                        "Hello",
                        "World"
                    ]
                }"""
            ),
            id="extract_array",
        ),
        pytest.param(
            "<html><body><h1>1</h1><h1>2</h1><h1>3</h1><h1>4</h1></body></html>",
            json.loads(
                """{
                    "h1_vals": [
                        "1",
                        "4"
                    ]
                }"""
            ),
            id="extract_array_non_contigous_elements",
        ),
        pytest.param(
            "<html><body><span>Test</span><h1>Hello</h1><h1>World</h1></body></html>",
            json.loads(
                """{
                    "some_key": "Test",
                    "h1_vals": [
                        "Hello",
                        "World"
                    ]
                }"""
            ),
            id="extract_string_and_array",
        ),
        pytest.param(
            "<html><body><h1>Title</h1><div><h2>Section Name</h2><a href='/a.html'>A</a><a href='/b.html'>B</a><a href='/c.html'>C</a></div></body></html>",
            json.loads(
                """{
                    "title": "Title",
                    "content": {
                        "name": "Section Name",
                        "pages": [
                            "A",
                            "B",
                            "C"
                        ]
                    }
                }"""
            ),
            id="extract_dict_values",
        ),
        pytest.param(
            "<html><body><table><th><td>Type</td><td>Column1</td><td>Column2</td></th><tr><td>A</td><td>11</td><td>12</td></tr><tr><td>B</td><td>21</td><td>22</td></tr></table></body></html>",
            json.loads(
                """{
                    "rows": [{
                        "type": "A",
                        "values": [
                            "11", 
                            "12"
                        ]
                    }, {
                        "type": "B",
                        "values": [
                            "21", 
                            "22"
                        ]
                    }]
                }"""
            ),
            id="extract_array_of_dicts",
        ),
        pytest.param(
            '<html><body><h1>My string has "double quotes" in it!</h1></body></html>',
            json.loads(
                """{
                    "str": "My string has \\"double quotes\\" in it!"
                }"""
            ),
            id="extract_string_with_double_quotes",
        ),
        pytest.param(
            "<html><body><h1>My string has 'single quotes' in it!</h1></body></html>",
            json.loads(
                """{
                    "str": "My string has 'single quotes' in it!"
                }"""
            ),
            id="extract_string_with_single_quotes",
        ),
    ],
)
def test_path_extraction_succeeds(html, targets):
    matcher_paths = StructuredPathGenerator(html).match(targets)

    scraped_data = StructuredPathScraper(html).fetch(matcher_paths)
    assert scraped_data == targets


@pytest.mark.parametrize(
    ("html", "targets"),
    [
        pytest.param(
            "<html><body><h1>My string has 'single quotes' and \"double quotes\" in it!</h1></body></html>",
            json.loads(
                """{
                    "str": "My string has 'single quotes' and \\"double quotes\\" in it!"
                }"""
            ),
            id="extract_string_with_single_quotes_and_double_quotes",
        ),
    ],
)
def test_path_extraction_fails_not_implemented(html, targets):
    with pytest.raises(NotImplementedError):
        StructuredPathGenerator(html).match(targets)
