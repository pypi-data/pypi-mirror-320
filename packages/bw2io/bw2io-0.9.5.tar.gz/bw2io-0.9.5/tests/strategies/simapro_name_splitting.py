import re

from bw2io.strategies.simapro import (
    detoxify_pattern,
    split_simapro_name_geo,
    split_simapro_name_geo_curly_brackets,
)


detoxify_re = re.compile(detoxify_pattern)


def test_detoxify_re():
    assert not detoxify_re.search("Cheese U")
    assert not detoxify_re.search("Cheese/CH")
    assert detoxify_re.search("Cheese/CH U")
    assert detoxify_re.search("Cheese/CH/I U")
    assert detoxify_re.search("Cheese/CH/I S")
    assert detoxify_re.search("Cheese/RER U")
    assert detoxify_re.search("Cheese/CENTREL U")
    assert detoxify_re.search("Cheese/CENTREL S")


def test_detoxify_re2():
    test_strings = [
        "Absorption chiller 100kW/CH/I U",
        "Absorption chiller 100kW /CH/I U",
        "Disposal, solvents mixture, 16.5% water, to hazardous waste incineration/CH U",
        "Electricity, at power plant/hard coal, IGCC, no CCS/2025/RER U",
        "Electricity, natural gas, at fuel cell SOFC 200kWe, alloc exergy, 2030/CH U",
        "Heat exchanger/of cogen unit 160kWe/RER/I U",
        "Lignite, burned in power plant/post, pipeline 200km, storage 1000m/2025/RER U",
        "Transport, lorry >28t, fleet average/CH U",
        "Water, cooling, unspecified natural origin, CH",
        "Water, cooling, unspecified natural origin/m3",
        "Water/m3",
    ]

    expected_results = [
        [("Absorption chiller 100kW", "CH", "/I")],
        [("Absorption chiller 100kW ", "CH", "/I")],
        [
            (
                "Disposal, solvents mixture, 16.5% water, to hazardous waste incineration",
                "CH",
                "",
            )
        ],
        [
            (
                "Electricity, at power plant/hard coal, IGCC, no CCS/2025",
                "RER",
                "",
            )
        ],
        [
            (
                "Electricity, natural gas, at fuel cell SOFC 200kWe, alloc exergy, 2030",
                "CH",
                "",
            )
        ],
        [("Heat exchanger/of cogen unit 160kWe", "RER", "/I")],
        [
            (
                "Lignite, burned in power plant/post, pipeline 200km, storage 1000m/2025",
                "RER",
                "",
            )
        ],
        [("Transport, lorry >28t, fleet average", "CH", "")],
        [],
        [],
        [],
    ]
    for string, result in zip(test_strings, expected_results):
        assert detoxify_re.findall(string) == result


def test_splitting_datasets():
    db = [
        {"name": "Absorption chiller 100kW/CH/I U"},
        {"name": "Absorption chiller 100kW /CH/I U"},
        {"name": "Cheese/CH"},
    ]
    result = [
        {
            "name": "Absorption chiller 100kW",
            "location": "CH",
            "reference product": "Absorption chiller 100kW",
            "simapro name": "Absorption chiller 100kW/CH/I U",
        },
        {
            "name": "Absorption chiller 100kW",
            "location": "CH",
            "reference product": "Absorption chiller 100kW",
            "simapro name": "Absorption chiller 100kW /CH/I U",
        },
        {"name": "Cheese/CH"},
    ]
    assert split_simapro_name_geo(db) == result


def test_splitting_exchanges():
    db = [
        {
            "name": "foo",
            "exchanges": [
                {"name": "Absorption chiller 100kW/CH/I U"},
                {"name": "Cheese/CH"},
            ],
        },
        {
            "name": "foo",
            "exchanges": [
                {"name": "Absorption chiller 100kW /CH/I U"},
                {"name": "Cheese/CH"},
            ],
        },
    ]
    result = [
        {
            "name": "foo",
            "exchanges": [
                {
                    "name": "Absorption chiller 100kW",
                    "location": "CH",
                    "simapro name": "Absorption chiller 100kW/CH/I U",
                },
                {"name": "Cheese/CH"},
            ],
        },
        {
            "name": "foo",
            "exchanges": [
                {
                    "name": "Absorption chiller 100kW",
                    "location": "CH",
                    "simapro name": "Absorption chiller 100kW /CH/I U",
                },
                {"name": "Cheese/CH"},
            ],
        },
    ]
    assert split_simapro_name_geo(db) == result


def test_split_simapro_name_geo_curly_brackets_custom_suffix():
    given = [
        {
            "name": "Wheat straw, at farm {NL} Energy, U",
            "exchanges": [{"name": "Wheat straw, at farm{NL}Energy, U "}],
        },
        {
            "name": "Dairy cows ration, at farm {ES}Energy, U",
            "simapro name": "foo",
            "exchanges": [
                {
                    "name": "Dairy cows ration, at farm {IAI Area, South America}Energy, U\t"
                }
            ],
        },
    ]
    expected = [
        {
            "name": "Wheat straw, at farm",
            "location": "NL",
            "simapro name": "Wheat straw, at farm {NL} Energy, U",
            "exchanges": [
                {
                    "simapro name": "Wheat straw, at farm{NL}Energy, U ",
                    "name": "Wheat straw, at farm",
                    "location": "NL",
                }
            ],
        },
        {
            "name": "Dairy cows ration, at farm",
            "location": "ES",
            "simapro name": "foo",
            "exchanges": [
                {
                    "simapro name": "Dairy cows ration, at farm {IAI Area, South America}Energy, U\t",
                    "name": "Dairy cows ration, at farm",
                    "location": "IAI Area, South America",
                }
            ],
        },
    ]
    result = split_simapro_name_geo_curly_brackets(given, "Energy, U")
    print(result)
    assert result == expected
