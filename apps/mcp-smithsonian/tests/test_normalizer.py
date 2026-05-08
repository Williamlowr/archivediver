import pytest
from tests.fixtures import APOLLO_ROW_WITH_IMAGE, ROW_NO_IMAGE
from mcp_smithsonian.normalizer import extract_media, normalize_row, _first_usable_media


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


# extract_media

def test_extract_media_with_image():
    media = extract_media("edanmdm:chndm_1901-39-3309", APOLLO_ROW_WITH_IMAGE)
    assert media.item_id == "edanmdm:chndm_1901-39-3309"
    assert media.title == "Thirteen Apollo Subjects for Ceiling"
    assert media.creator_display == "Felice Giani, Italian, 1758-1823"
    assert media.image_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_screen"
    assert media.thumbnail_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_thumb"
    assert media.image_download_url == "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001.jpg"
    assert media.image_alt == "THIRTEEN APOLLO SUBJECTS FOR CEILING"
    assert media.source_url == "https://collection.cooperhewitt.org/view/objects/asitem/id/10032"
    assert media.rights == "CC0"
    assert media.unit_code == "CHNDM"
    assert media.unit_name == "Cooper Hewitt, Smithsonian Design Museum"


def test_extract_media_no_image_returns_empty_fields():
    media = extract_media("edanmdm:sil_123", ROW_NO_IMAGE)
    assert media.item_id == "edanmdm:sil_123"
    assert media.image_url == ""
    assert media.thumbnail_url == ""
    assert media.image_download_url == ""
    assert media.image_alt == ""


def test_extract_media_empty_row_returns_empty_fields():
    media = extract_media("edanmdm:test_empty", {})
    assert media.item_id == "edanmdm:test_empty"
    assert media.image_url == ""
    assert media.source_url == ""
    assert media.title == ""
