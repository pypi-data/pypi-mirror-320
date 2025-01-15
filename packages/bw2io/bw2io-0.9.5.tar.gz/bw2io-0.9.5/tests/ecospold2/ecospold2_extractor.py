from pathlib import Path
from lxml import objectify
import pytest

from bw2io.extractors.ecospold2 import Ecospold2DataExtractor, getattr2

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "ecospold2"


def test_extraction_without_synonyms():
    data = Ecospold2DataExtractor.extract(
        FIXTURES
        / "00000_11111111-2222-3333-4444-555555555555_66666666-7777-8888-9999-000000000000.spold",
        "ei",
    )
    expected = {
        "comment": "Things and stuff and whatnot\na Kikki comment\nIncluded activities start:  Includes start stuff\nIncluded activities end:  Includes end stuff\nTechnology:  typical technology for ze Germans!",
        "classifications": [
            ("EcoSpold01Categories", "construction materials/concrete"),
            (
                "ISIC rev.4 ecoinvent",
                "2395:Manufacture of articles of concrete, cement and plaster",
            ),
        ],
        "activity type": "ordinary transforming activity",
        "activity": "c40e3c0a-292f-45a5-88cd-ed18265cb7d7",
        "database": "ei",
        "exchanges": [
            {
                "flow": "6fe4040b-39c7-4d58-b95b-6ee1de4aedb3",
                "type": "technosphere",
                "name": "clay pit infrastructure",
                "classifications": {
                    "By-product classification": "allocatable product",
                    "CPC": "53269: Other constructions for manufacturing",
                },
                "production volume": 0.0,
                "properties": {},
                "activity": "759fac54-b912-4781-9833-0ddd6e8cda24",
                "unit": "unit",
                "comment": "estimated",
                "amount": 9999.0,
                "pedigree": {
                    "reliability": 1,
                    "completeness": 1,
                    "temporal correlation": 5,
                    "geographical correlation": 1,
                    "further technological correlation": 1,
                },
                "uncertainty type": 2,
                "loc": 0.0,
                "scale": 0.4472135954999579,
                "scale without pedigree": 0.31622776601683794,
            },
            {
                "flow": "d4ee8f39-342b-4443-bbb9-c49b6801b5d6",
                "type": "production",
                "name": "concrete block",
                "classifications": {
                    "By-product classification": "allocatable product",
                    "CPC": "37510: Non-refractory mortars and concretes",
                },
                "production volume": 42.0,
                "properties": {
                    "carbon content, non-fossil": {
                        "amount": 0.0,
                        "unit": "dimensionless",
                    },
                    "water content": {
                        "amount": 1.0,
                        "unit": "dimensionless",
                        "comment": "water mass/dry mass",
                    },
                    "dry mass": {"amount": 2.0, "unit": "kg"},
                    "price": {"amount": 11.0, "unit": "EUR2005"},
                },
                "activity": None,
                "unit": "kg",
                "amount": 1.0,
                "uncertainty type": 0,
                "loc": 1.0,
            },
            {
                "flow": "075e433b-4be4-448e-9510-9a5029c1ce94",
                "type": "biosphere",
                "chemical formula": "h2o2",
                "formula": "does_it_hurt_when_dropped_on_foot * 2",
                "CAS number": "7732-18-5",
                "variable name": "it_is_boring_to_do_this_manually",
                "name": "Water",
                "classifications": {},
                "production volume": 0.0,
                "properties": {
                    "water in wet mass": {
                        "amount": 1000.0,
                        "unit": "kg",
                        "comment": "water content on a wet matter basis",
                    }
                },
                "unit": "m3",
                "comment": "Calculated value based on literature values and, like, experts, and stuff.",
                "amount": 123456.0,
                "pedigree": {
                    "reliability": 2,
                    "completeness": 2,
                    "temporal correlation": 5,
                    "geographical correlation": 1,
                    "further technological correlation": 1,
                },
                "uncertainty type": 2,
                "loc": 8.0,
                "scale": 2.449489742783178,
                "scale without pedigree": 2.6457513110645907,
            },
        ],
        "filename": "00000_11111111-2222-3333-4444-555555555555_66666666-7777-8888-9999-000000000000.spold",
        "location": "DE",
        "name": "concrete block production",
        "synonyms": [],
        "parameters": {
            "does_it_hurt_when_dropped_on_foot": {
                "description": "How much owwies PLEASE DON'T TELL MOM",
                "id": "daadf2d4-7bbb-4f69-8ab5-58df4c1685eb",
                "unit": "dimensionless",
                "comment": "This is where the people type the words!!!",
                "amount": 7777.0,
                "pedigree": {
                    "reliability": 4,
                    "completeness": 4,
                    "temporal correlation": 3,
                    "geographical correlation": 2,
                    "further technological correlation": 4,
                },
                "uncertainty type": 2,
                "loc": 2.0,
                "scale": 2.0,
                "scale without pedigree": 1.7320508075688772,
            }
        },
        "authors": {
            "data entry": {"name": "Don Ron Bon-Bon", "email": "yummy@example.org"},
            "data generator": {"name": "Rhyme Thyme", "email": "spicy@exaxmple.org"},
        },
        "type": "process",
    }
    assert data[0] == expected


def test_extraction_with_synonyms():
    data = Ecospold2DataExtractor.extract(
        FIXTURES
        / "00000_11111111-2222-3333-4444-555555555555_66666666-7777-8888-9999-000000000000_with_synonyms.spold",
        "ei",
    )
    expected = {
        "comment": "Things and stuff and whatnot\na Kikki comment\nIncluded activities end:  Includes some stuff\nTechnology:  typical technology for ze Germans!",
        "classifications": [
            ("EcoSpold01Categories", "construction materials/concrete"),
            (
                "ISIC rev.4 ecoinvent",
                "2395:Manufacture of articles of concrete, cement and plaster",
            ),
        ],
        "activity type": "ordinary transforming activity",
        "activity": "c40e3c0a-292f-45a5-88cd-ed18265cb7d7",
        "database": "ei",
        "exchanges": [
            {
                "flow": "6fe4040b-39c7-4d58-b95b-6ee1de4aedb3",
                "type": "technosphere",
                "name": "clay pit infrastructure",
                "classifications": {
                    "By-product classification": "allocatable product",
                    "CPC": "53269: Other constructions for manufacturing",
                },
                "production volume": 0.0,
                "properties": {},
                "activity": "759fac54-b912-4781-9833-0ddd6e8cda24",
                "unit": "unit",
                "comment": "estimated",
                "amount": 9999.0,
                "pedigree": {
                    "reliability": 1,
                    "completeness": 1,
                    "temporal correlation": 5,
                    "geographical correlation": 1,
                    "further technological correlation": 1,
                },
                "uncertainty type": 2,
                "loc": 0.0,
                "scale": 0.4472135954999579,
                "scale without pedigree": 0.31622776601683794,
            },
            {
                "flow": "d4ee8f39-342b-4443-bbb9-c49b6801b5d6",
                "type": "production",
                "name": "concrete block",
                "classifications": {
                    "By-product classification": "allocatable product",
                    "CPC": "37510: Non-refractory mortars and concretes",
                },
                "production volume": 42.0,
                "properties": {
                    "carbon content, non-fossil": {
                        "amount": 0.0,
                        "unit": "dimensionless",
                    },
                    "water content": {
                        "amount": 1.0,
                        "unit": "dimensionless",
                        "comment": "water mass/dry mass",
                    },
                    "dry mass": {"amount": 2.0, "unit": "kg"},
                    "price": {"amount": 11.0, "unit": "EUR2005"},
                },
                "activity": None,
                "unit": "kg",
                "amount": 1.0,
                "uncertainty type": 0,
                "loc": 1.0,
            },
            {
                "flow": "075e433b-4be4-448e-9510-9a5029c1ce94",
                "type": "biosphere",
                "name": "Water",
                "chemical formula": "h2o2",
                "formula": "does_it_hurt_when_dropped_on_foot * 2",
                "CAS number": "7732-18-5",
                "classifications": {},
                "variable name": "it_is_boring_to_do_this_manually",
                "production volume": 0.0,
                "properties": {
                    "water in wet mass": {
                        "amount": 1000.0,
                        "unit": "kg",
                        "comment": "water content on a wet matter basis",
                    }
                },
                "unit": "m3",
                "comment": "Calculated value based on literature values and, like, experts, and stuff.",
                "amount": 123456.0,
                "pedigree": {
                    "reliability": 2,
                    "completeness": 2,
                    "temporal correlation": 5,
                    "geographical correlation": 1,
                    "further technological correlation": 1,
                },
                "uncertainty type": 2,
                "loc": 8.0,
                "scale": 2.449489742783178,
                "scale without pedigree": 2.6457513110645907,
            },
        ],
        "filename": "00000_11111111-2222-3333-4444-555555555555_66666666-7777-8888-9999-000000000000_with_synonyms.spold",
        "location": "DE",
        "name": "concrete block production",
        "synonyms": ["concrete slab production", "concrete block manufacturing"],
        "parameters": {
            "does_it_hurt_when_dropped_on_foot": {
                "description": "How much owwies PLEASE DON'T TELL MOM",
                "id": "daadf2d4-7bbb-4f69-8ab5-58df4c1685eb",
                "unit": "dimensionless",
                "comment": "This is where the people type the words!!!",
                "amount": 7777.0,
                "pedigree": {
                    "reliability": 4,
                    "completeness": 4,
                    "temporal correlation": 3,
                    "geographical correlation": 2,
                    "further technological correlation": 4,
                },
                "uncertainty type": 2,
                "loc": 2.0,
                "scale": 2.0,
                "scale without pedigree": 1.7320508075688772,
            }
        },
        "authors": {
            "data entry": {"name": "Don Ron Bon-Bon", "email": "yummy@example.org"},
            "data generator": {"name": "Rhyme Thyme", "email": "spicy@exaxmple.org"},
        },
        "type": "process",
    }
    print(data[0])
    assert data[0] == expected


@pytest.fixture(
    params=[
        ["Things and stuff and whatnot", "a Kiki comment", ""],
        ["Things and stuff and whatnot", "", "a Kiki comment"],
        ["Things and stuff and whatnot", "", "a Kiki comment", "a Bouba comment"],
        [""],
    ]
)
def activity_multiline_gc(request):
    # Define namespaces and schema location
    ns = "http://www.EcoInvent.org/EcoSpold02"
    xsi_ns = "http://www.w3.org/2001/XMLSchema-instance"

    # Create the ecoSpold element with namespaces and schema location
    eco_spold = objectify.Element(
        "ecoSpold",
        nsmap={
            None: ns,  # Default namespace
            "xsi": xsi_ns,
        },
    )
    eco_spold.set(
        f"{{{xsi_ns}}}schemaLocation",
        "http://www.EcoInvent.org/EcoSpold02 ../../schemas/datasets/EcoSpold02.xsd "
        "http://www.EcoInvent.org/UsedUserMasterData ../../schemas/datasets/EcoSpold02UserMasterData.xsd",
    )

    # Create the activity element
    activity = objectify.SubElement(eco_spold, "activity")

    # Create the generalComment element
    general_comment = objectify.SubElement(activity, "generalComment")

    # Add text elements to generalComment
    for i, a_text in enumerate(request.param):
        text_e = objectify.SubElement(general_comment, f"{{{ns}}}text", index=f"{i}")
        text_e.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
        text_e._setText(a_text)

    return activity


def test_condense_multiline_comment(request, activity_multiline_gc):
    expected = "\n".join(
        [s for s in request.node.callspec.params.get("activity_multiline_gc") if s]
    )
    res = Ecospold2DataExtractor.condense_multiline_comment(
        getattr2(activity_multiline_gc, "generalComment")
    )
    assert res == expected
