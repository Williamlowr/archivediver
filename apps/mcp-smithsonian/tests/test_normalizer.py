import pytest
from tests.fixtures import APOLLO_ROW_WITH_IMAGE, ROW_NO_IMAGE
from mcp_smithsonian.normalizer import normalize_row, _first_usable_media


def test_normalize_full_row():
    artifact = normalize_row(APOLLO_ROW_WITH_IMAGE)
    assert artifact is not None
    assert artifact.id == "edanmdm:chndm_1901-39-3309"
    assert artifact.record_id == "chndm_1901-39-3309"
    assert artifact.title == "Thirteen Apollo Subjects for Ceiling"
    assert artifact.date_display == "early 19th century"
    assert artifact.date_indexed == ["1800s"]
    assert artifact.creator_display == "Felice Giani, Italian, 1758-1823"
    assert artifact.description == "Center, octagonal representation of Apollo and Muses."
    assert artifact.object_type == "Drawings"
    assert artifact.unit_code == "CHNDM"
    assert artifact.unit_name == "Cooper Hewitt, Smithsonian Design Museum"
    assert artifact.source_url == "https://collection.cooperhewitt.org/view/objects/asitem/id/10032"
    assert artifact.image_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_screen"
    assert artifact.thumbnail_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_thumb"
    assert artifact.image_download_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001.jpg"
    assert artifact.image_alt == "THIRTEEN APOLLO SUBJECTS FOR CEILING"
    assert artifact.rights == "CC0"
    assert artifact.place_tags == ["Italy"]
    assert artifact.subject_tags == []


def test_normalize_drops_row_without_image():
    artifact = normalize_row(ROW_NO_IMAGE)
    assert artifact is None


def test_normalize_missing_content():
    artifact = normalize_row({})
    assert artifact is None


def test_normalize_falls_back_to_row_title():
    row = dict(APOLLO_ROW_WITH_IMAGE)
    row = {**row, "content": {
        **row["content"],
        "descriptiveNonRepeating": {
            **row["content"]["descriptiveNonRepeating"],
            "title": {},
        },
    }}
    artifact = normalize_row(row)
    assert artifact is not None
    assert artifact.title == "Thirteen Apollo Subjects for Ceiling"


def test_first_usable_media_screen_image_wins():
    media_list = [
        {
            "resources": [
                {"label": "Screen Image", "url": "https://example.com/screen.jpg"},
                {"label": "High-resolution JPEG", "url": "https://example.com/hires.jpg"},
            ]
        }
    ]
    result = _first_usable_media(media_list)
    assert result is not None
    assert result[0] == "https://example.com/screen.jpg"
    assert result[2] == "https://example.com/hires.jpg"


def test_first_usable_media_falls_back_to_content():
    media_list = [{"content": "https://example.com/content.jpg", "thumbnail": ""}]
    result = _first_usable_media(media_list)
    assert result is not None
    assert result[0] == "https://example.com/content.jpg"


def test_first_usable_media_returns_none_if_no_url():
    result = _first_usable_media([{"resources": []}])
    assert result is None


def test_first_usable_media_skips_empty_entries():
    media_list = [
        {"resources": []},
        {"content": "", "thumbnail": ""},
        {"content": "https://example.com/second.jpg"},
    ]
    result = _first_usable_media(media_list)
    assert result is not None
    assert result[0] == "https://example.com/second.jpg"
