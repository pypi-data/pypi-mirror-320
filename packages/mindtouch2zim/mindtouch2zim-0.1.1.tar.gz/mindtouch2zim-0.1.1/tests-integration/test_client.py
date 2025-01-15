import io
import re

import pytest
from zimscraperlib.image.probing import format_for

from mindtouch2zim.client import (
    LibraryPageId,
    LibraryTree,
    MindtouchClient,
    MindtouchHome,
)
from mindtouch2zim.context import Context
from mindtouch2zim.download import stream_file

context = Context.get()


@pytest.fixture(scope="module")
def home(client: MindtouchClient) -> MindtouchHome:
    return client.get_home()


@pytest.fixture(scope="module")
def minimum_number_of_pages() -> int:
    return 8000


@pytest.fixture(scope="module")
def somewhere_page_id() -> LibraryPageId:
    return "15728"


@pytest.fixture(scope="module")
def nb_somewhere_children() -> int:
    return 5


@pytest.fixture(scope="module")
def root_page_id() -> LibraryPageId:
    return "34"


@pytest.fixture(scope="module")
def nb_root_children() -> int:
    return 6


@pytest.fixture(scope="module")
def page_tree(
    client: MindtouchClient,
) -> LibraryTree:
    return client.get_page_tree()


def test_get_deki_token(deki_token: str):
    """Ensures we achieve to get a deki_token"""
    assert deki_token


def test_get_all_pages_ids(
    client: MindtouchClient,
    minimum_number_of_pages: int,
):
    pages_ids = client.get_all_pages_ids()
    assert len(pages_ids) > minimum_number_of_pages


def test_get_page_tree_pages(
    page_tree: LibraryTree,
    minimum_number_of_pages: int,
):
    assert len(page_tree.pages.keys()) > minimum_number_of_pages


def test_get_page_tree_root(
    page_tree: LibraryTree,
    root_page_id: str,
    nb_root_children: int,
):
    assert page_tree.root.id == root_page_id
    assert len(page_tree.root.children) == nb_root_children
    assert page_tree.root.title
    for child in page_tree.root.children:
        assert child.title


def test_get_page_tree_subtree(
    page_tree: LibraryTree,
):

    # 28207 = https://geo.libretexts.org/Courses/Coastline_College/An_Introduction_To_Geology_-_Coastline_College/01%3A_Understanding_Science
    subtree1 = page_tree.sub_tree("28207")
    # 4 = "1. Understransding Science" + "1.1: What is Science?"
    #  + "1.2: The Scientific Method" + "1.3: The Study of Geology"
    assert len(subtree1.pages.keys()) == 4

    # 28196 = https://geo.libretexts.org/Courses/Coastline_College/An_Introduction_To_Geology_-_Coastline_College
    subtree2 = page_tree.sub_tree("28196")
    # 94 is number retrieved in Oct. 2024, might change
    assert len(subtree2.pages.keys()) == 94


def test_get_page_tree_somewhere(
    client: MindtouchClient,
    somewhere_page_id: str,
    nb_somewhere_children: int,
):
    page_tree = client.get_page_tree(somewhere_page_id)
    assert page_tree.root.id == somewhere_page_id
    assert len(page_tree.root.children) == nb_somewhere_children
    assert page_tree.root.title
    for child in page_tree.root.children:
        assert child.title


def test_get_home_image_url(home: MindtouchHome):
    """Ensures proper image url is retrieved"""
    assert home.welcome_image_url == "https://cdn.libretexts.net/Logos/geo_full.png"


def test_get_home_image_size(home: MindtouchHome, home_png_size: int):
    """Ensures image url is retrievable"""
    dst = io.BytesIO()
    stream_file(home.welcome_image_url, byte_stream=dst)
    assert format_for(dst, from_suffix=False) == "PNG"
    assert len(dst.getvalue()) == home_png_size


def test_get_home_welcome_text_paragraphs(
    home: MindtouchHome, home_welcome_text_paragraphs: list[str]
):
    """Ensures proper data is retrieved from home of libretexts"""

    assert home.welcome_text_paragraphs == home_welcome_text_paragraphs


def test_get_home_page_content(client: MindtouchClient, page_tree: LibraryTree):
    """Ensures we can get content of root page"""
    assert client.get_page_content(page_tree.root).html_body


def test_get_index_page_from_template(
    client: MindtouchClient,
    page_tree: LibraryTree,
):
    """Ensures we can get content of an index page"""
    page_15837 = page_tree.sub_tree("15837").root
    cover_page_id = client.get_cover_page_id(page_15837)
    assert cover_page_id
    assert client.get_template_content(
        page_id=cover_page_id,
        template="=Template%253AMindTouch%252FIDF3%252FViews%252FTag_directory",
    )


def test_get_cover_page_encoded_url(
    client: MindtouchClient,
    page_tree: LibraryTree,
):
    page_15837 = page_tree.sub_tree("15837").root
    assert (
        client.get_cover_page_encoded_url(page_15837)
        == "https://geo.libretexts.org/Courses/California_State_University_Los_Angeles/"
        "Book%3A_An_Introduction_to_Geology_(Johnson_Affolter_Inkenbrandt_and_Mosher)"
    )


@pytest.mark.parametrize(
    "current_id, expected_cover_page_id",
    [
        ("15837", "15718"),
        (":0794f6ff8238481ab880b6484deb65f4", "15718"),
        ("15844", None),
        ("34", None),
        ("home", None),
    ],
)
def test_get_cover_page_id_by_id(
    client: MindtouchClient,
    current_id: str,
    expected_cover_page_id: str | None,
):
    assert client.get_cover_page_id(current_id) == expected_cover_page_id


@pytest.mark.parametrize(
    "current_id, expected_cover_page_id",
    [("15837", "15718"), ("15844", None), ("34", None)],
)
def test_get_cover_page_id_by_page(
    client: MindtouchClient,
    page_tree: LibraryTree,
    current_id: str,
    expected_cover_page_id: str | None,
):
    page_object = page_tree.sub_tree(current_id).root
    assert client.get_cover_page_id(page_object) == expected_cover_page_id


def test_get_home_screen_css_url(home: MindtouchHome):
    """Ensures proper screen CSS url is retrieved"""
    assert re.match(
        r"https:\/\/a\.mtstatic\.com\/@cache\/layout\/anonymous\.css\?_=.*:site_4038",
        home.screen_css_url,
    )


def test_get_home_print_css_url(home: MindtouchHome):
    """Ensures proper print CSS url is retrieved"""
    assert re.match(
        r"https:\/\/a\.mtstatic\.com\/@cache\/layout\/print\.css\?_=.*:site_4038",
        home.print_css_url,
    )


def test_get_home_inline_css(home: MindtouchHome):
    """Ensures proper print CSS url is retrieved"""
    assert len(home.inline_css) >= 10  # 13 expected as of Oct. 2024
    assert len("\n".join(home.inline_css)) >= 35000  # 39843 expected as of Oct. 2024


def test_get_home_url(home: MindtouchHome, libretexts_url: str):
    assert home.home_url == f"{libretexts_url}/"


def test_get_home_icons_urls(home: MindtouchHome, home_icons_urls: list[str]):
    """Ensures proper icons urls are retrieved from home of libretexts"""
    assert home.icons_urls == home_icons_urls
