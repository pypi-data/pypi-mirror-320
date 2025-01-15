from stats_arrays import LognormalUncertainty

from bw2io.strategies.simapro import *


def test_set_lognormal_loc_value_uncertainty_safe():
    given = [
        {
            "exchanges": [
                {
                    "type": "foo",
                    "name": "Water, BR",
                    "uncertainty type": LognormalUncertainty.id,
                    "amount": 1,
                    "loc": 1,
                    "scale": 0.1,
                }
            ]
        }
    ]
    expected = [
        {
            "exchanges": [
                {
                    "type": "foo",
                    "name": "Water, BR",
                    "uncertainty type": LognormalUncertainty.id,
                    "amount": 1,
                    "loc": 0,
                    "scale": 0.1,
                }
            ]
        }
    ]
    assert set_lognormal_loc_value_uncertainty_safe(given) == expected


def test_localized_water_flows():
    given = [
        {
            "exchanges": [
                {
                    "type": "foo",
                    "name": "Water, BR",
                },
                {
                    "input": True,
                    "name": "Water, BR",
                },
                {"type": "biosphere", "name": "Not Water, BR"},
                {
                    "type": "biosphere",
                    "name": "Water, turbine use, unspecified natural origin, UCTE without Germany and France",
                },
                {
                    "type": "biosphere",
                    "name": "Water, river, Québec, HQ distribution network",
                },
                {
                    "type": "biosphere",
                    "name": "Water, well, in ground, IAI Area, Asia, without China and GCC",
                },
                {
                    "type": "biosphere",
                    "name": "Water, unspecified natural origin, IAI Area 4&5 without China",
                },
                {"type": "biosphere", "name": "Water, unspecified natural origin, HU"},
            ]
        }
    ]
    expected = [
        {
            "exchanges": [
                {
                    "type": "foo",
                    "name": "Water, BR",
                },
                {
                    "input": True,
                    "name": "Water, BR",
                },
                {"type": "biosphere", "name": "Not Water, BR"},
                {
                    "type": "biosphere",
                    "name": "Water, turbine use, unspecified natural origin",
                    "simapro location": "UCTE without Germany and France",
                },
                {
                    "type": "biosphere",
                    "name": "Water, river",
                    "simapro location": "Québec, HQ distribution network",
                },
                {
                    "type": "biosphere",
                    "name": "Water, well, in ground",
                    "simapro location": "IAI Area, Asia, without China and GCC",
                },
                {
                    "type": "biosphere",
                    "name": "Water, unspecified natural origin",
                    "simapro location": "IAI Area, Asia, without China and GCC",
                },
                {
                    "type": "biosphere",
                    "name": "Water, unspecified natural origin",
                    "simapro location": "HU",
                },
            ]
        }
    ]
    assert fix_localized_water_flows(given) == expected


def test_change_electricity_units():
    given = [
        {
            "exchanges": [
                {
                    "name": "market for electricity, etc.",
                    "unit": "kilowatt hour",
                    "amount": 1,
                },
                {
                    "name": "electricity, blah blah blah",
                    "unit": "megajoule",
                    "amount": 7.2,
                },
                {
                    "name": "market for electricity, do be do be dooooo",
                    "unit": "megajoule",
                    "amount": 3.6,
                },
                {
                    "name": "market group for electricity, do be do be dooooo",
                    "unit": "megajoule",
                    "amount": 3.6,
                },
            ]
        }
    ]
    expected = [
        {
            "exchanges": [
                {
                    "name": "market for electricity, etc.",
                    "unit": "kilowatt hour",
                    "amount": 1,
                },
                {
                    "name": "electricity, blah blah blah",
                    "unit": "kilowatt hour",
                    "amount": 2,
                    "loc": 2,
                },
                {
                    "name": "market for electricity, do be do be dooooo",
                    "unit": "kilowatt hour",
                    "amount": 1,
                    "loc": 1,
                },
                {
                    "name": "market group for electricity, do be do be dooooo",
                    "unit": "kilowatt hour",
                    "amount": 1,
                    "loc": 1,
                },
            ]
        }
    ]
    assert change_electricity_unit_mj_to_kwh(given) == expected


def test_fix_zero_allocation_products():
    given = [
        {
            "exchanges": [
                {"type": "production", "amount": 0},
                {"type": "technosphere", "amount": 1},
            ]
        },
        {
            "exchanges": [
                {"type": "production", "amount": 0},
                {"type": "production", "amount": 0},
                {"type": "technosphere", "amount": 1},
            ]
        },
        {
            "exchanges": [
                {"type": "production", "amount": 1},
                {"type": "technosphere", "amount": 1},
            ]
        },
    ]
    expected = [
        {
            "exchanges": [
                {"type": "production", "amount": 1, "loc": 1, "uncertainty type": 0}
            ]
        },
        {
            "exchanges": [
                {"type": "production", "amount": 0},
                {"type": "production", "amount": 0},
                {"type": "technosphere", "amount": 1},
            ]
        },
        {
            "exchanges": [
                {"type": "production", "amount": 1},
                {"type": "technosphere", "amount": 1},
            ]
        },
    ]
    assert fix_zero_allocation_products(given) == expected


def test_set_metadata_using_single_functional_exchange():
    given = [
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
        },
        {
            "exchanges": [{"functional": True, "amount": 42}],
        },
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
            "name": "(unknown)",
            "reference product": "(unknown)",
            "unit": "(unknown)",
        },
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
            "name": "a",
            "reference product": "b",
            "unit": "c",
            "production amount": 7,
        },
        {"exchanges": [{"functional": True}, {"functional": True}]},
    ]
    expected = [
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
            "name": "foo",
            "reference product": "foo",
            "unit": "kg",
            "production amount": 42,
        },
        {
            "exchanges": [{"functional": True, "amount": 42}],
            "production amount": 42,
            "name": "(unknown)",
            "reference product": "(unknown)",
            "unit": "(unknown)",
        },
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
            "name": "foo",
            "reference product": "foo",
            "unit": "kg",
            "production amount": 42,
        },
        {
            "exchanges": [
                {"functional": True, "amount": 42, "name": "foo", "unit": "kg"}
            ],
            "name": "a",
            "reference product": "b",
            "unit": "c",
            "production amount": 7,
        },
        {"exchanges": [{"functional": True}, {"functional": True}]},
    ]
    assert set_metadata_using_single_functional_exchange(given) == expected


def test_override_process_name_using_single_functional_exchange():
    given = [
        {
            "name": "replace me",
            "exchanges": [{"functional": True, "name": "foo"}],
        },
        {
            "name": "replace me",
            "exchanges": [{"functional": True}],
        },
        {
            "name": "replace me",
            "exchanges": [{"functional": True, "name": "(unknown)"}],
        },
    ]
    expected = [
        {
            "name": "foo",
            "exchanges": [{"functional": True, "name": "foo"}],
        },
        {
            "name": "replace me",
            "exchanges": [{"functional": True}],
        },
        {
            "name": "replace me",
            "exchanges": [{"functional": True, "name": "(unknown)"}],
        },
    ]
    assert override_process_name_using_single_functional_exchange(given) == expected


def test_normalize_simapro_labels_to_brightway_standard():
    given = [
        {
            "exchanges": [
                {"input": True, "context": "something"},
                {
                    "context": ["foo"],
                },
                {"identifier": "abcde"},
            ]
        }
    ]
    expected = [
        {
            "exchanges": [
                {"input": True, "context": "something"},
                {
                    "categories": ("foo",),
                    "context": ["foo"],
                },
                {"code": "abcde", "identifier": "abcde"},
            ]
        }
    ]
    assert normalize_simapro_labels_to_brightway_standard(given) == expected


def test_remove_biosphere_location_prefix_if_flow_in_same_location():
    given = [
        {
            "location": "FR",
            "exchanges": [
                {
                    "name": "Water, unspecified natural origin, RO",
                    "type": "biosphere",
                },
                {
                    "name": "Transformation, to permanent crop, FR",
                    "type": "biosphere",
                },
                {
                    "name": "Phosphorus, FR",
                    "type": "biosphere",
                },
                {
                    "name": "Phosphorus FR",
                    "type": "biosphere",
                },
                {
                    "name": "Phosphorus/ FR",
                    "type": "biosphere",
                },
            ],
        },
        {
            "location": "IAI Area, South America",
            "exchanges": [
                {
                    "name": "Transformation, to permanent crop, IAI Area, South America",
                    "type": "biosphere",
                }
            ],
        },
    ]
    expected = [
        {
            "location": "FR",
            "exchanges": [
                {
                    "name": "Water, unspecified natural origin, RO",
                    "type": "biosphere",
                },
                {
                    "name": "Transformation, to permanent crop",
                    "simapro name": "Transformation, to permanent crop, FR",
                    "type": "biosphere",
                },
                {
                    "simapro name": "Phosphorus, FR",
                    "name": "Phosphorus",
                    "type": "biosphere",
                },
                {
                    "simapro name": "Phosphorus FR",
                    "name": "Phosphorus",
                    "type": "biosphere",
                },
                {
                    "simapro name": "Phosphorus/ FR",
                    "name": "Phosphorus",
                    "type": "biosphere",
                },
            ],
        },
        {
            "location": "IAI Area, South America",
            "exchanges": [
                {
                    "simapro name": "Transformation, to permanent crop, IAI Area, South America",
                    "name": "Transformation, to permanent crop",
                    "type": "biosphere",
                }
            ],
        },
    ]
    result = remove_biosphere_location_prefix_if_flow_in_same_location(given)
    assert result == expected
