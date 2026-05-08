"""Shared test fixtures for mcp-smithsonian tests."""

APOLLO_ROW_WITH_IMAGE: dict = {
    "id": "chndm_1901-39-3309",
    "url": "edanmdm:chndm_1901-39-3309",
    "title": "Thirteen Apollo Subjects for Ceiling",
    "unitCode": "CHNDM",
    "type": "edanmdm",
    "content": {
        "descriptiveNonRepeating": {
            "record_ID": "chndm_1901-39-3309",
            "unit_code": "CHNDM",
            "data_source": "Cooper Hewitt, Smithsonian Design Museum",
            "record_link": "https://collection.cooperhewitt.org/view/objects/asitem/id/10032",
            "title": {"label": "Title", "content": "Thirteen Apollo Subjects for Ceiling"},
            "online_media": {
                "mediaCount": 1,
                "media": [
                    {
                        "content": "https://ids.si.edu/ids/deliveryService?id=CHSDM-3D4BA7C1D0CE2-000001",
                        "thumbnail": "https://ids.si.edu/ids/deliveryService?id=CHSDM-3D4BA7C1D0CE2-000001_thumb",
                        "altTextAccessibility": "THIRTEEN APOLLO SUBJECTS FOR CEILING",
                        "resources": [
                            {
                                "label": "Screen Image",
                                "url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_screen",
                            },
                            {
                                "label": "High-resolution JPEG",
                                "url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001.jpg",
                            },
                            {
                                "label": "Thumbnail Image",
                                "url": "https://ids.si.edu/ids/download?id=CHSDM-3D4BA7C1D0CE2-000001_thumb",
                            },
                        ],
                    }
                ],
            },
        },
        "indexedStructured": {
            "date": ["1800s"],
            "object_type": ["Drawings"],
            "place": ["Italy"],
            "topic": [],
        },
        "freetext": {
            "date": [{"label": "Date", "content": "early 19th century"}],
            "name": [{"label": "Designer", "content": "Felice Giani, Italian, 1758-1823"}],
            "notes": [
                {
                    "label": "Description",
                    "content": "Center, octagonal representation of Apollo and Muses.",
                }
            ],
            "objectRights": [{"label": "Rights", "content": "CC0"}],
            "dataSource": [
                {"label": "Data Source", "content": "Cooper Hewitt, Smithsonian Design Museum"}
            ],
        },
    },
}

ROW_NO_IMAGE: dict = {
    "id": "sil_123",
    "url": "edanmdm:sil_123",
    "title": "No Image Item",
    "unitCode": "SIL",
    "type": "edanmdm",
    "content": {
        "descriptiveNonRepeating": {
            "record_ID": "sil_123",
            "unit_code": "SIL",
            "data_source": "Smithsonian Libraries",
            "record_link": "https://library.si.edu/test",
            "title": {"label": "Title", "content": "No Image Item"},
        },
        "indexedStructured": {
            "date": ["1900s"],
            "object_type": ["Books"],
            "online_media_type": ["Images"],
        },
        "freetext": {},
    },
}
