import os

from bw2data import Database, Method, config, get_node, methods
from bw2data.tests import bw2test

from bw2io import CSVLCIAImporter
from bw2io.extractors.csv import CSVExtractor

CSV_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "fixtures", "csv")


def test_csv_lcia_extraction():
    fp = os.path.join(CSV_FIXTURES_DIR, "lcia.csv")
    expected = [
        "lcia.csv",
        [
            ["name", "categories", "amount"],
            ["Aluminium", "Resource::in ground", "42"],
            ["Uranium ore, 1.11 GJ per kg", "Resource", "1000000"],
        ],
    ]
    assert CSVExtractor.extract(fp) == expected


@bw2test
def test_import_initial_data():
    fp = os.path.join(CSV_FIXTURES_DIR, "lcia.csv")
    expected = [
        {
            "name": ("foo",),
            "description": "",
            "filename": "lcia.csv",
            "unit": "bar",
            "exchanges": [
                {
                    "name": "Aluminium",
                    "categories": "Resource::in ground",
                    "amount": "42",
                },
                {
                    "name": "Uranium ore, 1.11 GJ per kg",
                    "categories": "Resource",
                    "amount": "1000000",
                },
            ],
        }
    ]
    eli = CSVLCIAImporter(fp, ("foo",), "", "bar")
    assert eli.data == expected


@bw2test
def test_csv_lcia_integration():
    Database("biosphere").write(
        {
            ("biosphere", "a"): {
                "name": "aluminium",
                "categories": ("Resource", "in ground"),
            },
            ("biosphere", "b"): {
                "name": "Uranium ore, 1.11 GJ per kg",
                "categories": ("Resource",),
            },
        }
    )
    config.p["biosphere_database"] = "biosphere"
    fp = os.path.join(CSV_FIXTURES_DIR, "lcia.csv")
    eli = CSVLCIAImporter(fp, ("foo",), "d", "bar")
    eli.apply_strategies()
    eli.write_methods()

    expected = {
        "abbreviation": "foo.acbd18db4cc2f85cedef654fccc4a4d8",
        "description": "d",
        "num_cfs": 2,
        "geocollections": ["world"],
        "filename": "lcia.csv",
        "unit": "bar",
    }
    assert methods[("foo",)] == expected

    expected = [(get_node(code="a").id, 42), (get_node(code="b").id, 1000000)]
    assert Method(("foo",)).load() == expected
