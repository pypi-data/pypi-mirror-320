from json import load
from pathlib import Path

from pytest import raises

from piscada_foresight.domains import (
    _validate_domains,
    get_domains,
    get_parent_traits,
    get_trait_by_id,
)
from piscada_foresight.model import Trait

DOMAINS_RESPONSE = load((Path(__file__).parent / "domains_response.json").open())


def test_get_domains(mocker):
    mock_client = mocker.Mock()
    mock_client.execute.return_value = DOMAINS_RESPONSE["data"]

    domains = get_domains(mock_client)

    assert len(domains) == 16  # noqa: PLR2004
    assert domains[2].name == "Brick"
    brick_domain = domains[2]
    assert brick_domain.prefix == "brick"
    assert brick_domain.uri == "https://brickschema.org/schema/Brick#"

    assert brick_domain.traits[2].id == "brick:Access_Control_Equipment"
    assert brick_domain.traits[2].parent_ids == ["brick:Security_Equipment"]
    assert brick_domain.traits[2].child_ids == ["brick:Access_Reader"]

    assert brick_domain.traits[6].id == "brick:AHU"
    assert brick_domain.traits[6].equivalent_ids == [
        "brick:Air_Handler_Unit",
        "brick:Air_Handling_Unit",
    ]

    assert brick_domain.relationships[0].id == "brick:feeds"
    assert brick_domain.relationships[0].parent_ids == [
        "fs_navigation:breadcrumbProcessIncoming",
        "fs_navigation:Expert",
        "fs_navigation:moreDetailsOrOutgoing",
        "fs_navigation:outgoing",
        "fs_navigation:Semantic",
        "fs_schema:Association",
    ]
    assert brick_domain.relationships[0].child_ids == ["brick:feedsAir"]
    assert brick_domain.relationships[0].inverse_ids == ["brick:isFedBy"]


def test_get_trait_by_id():
    """Test retrieving a trait by ID from a domain."""
    domains = _validate_domains(DOMAINS_RESPONSE["data"])
    assert len(domains) == 16  # noqa: PLR2004
    assert domains[2].name == "Brick"
    brick_domain = domains[2]
    retrieved_trait = brick_domain.get_trait_by_id("brick:Building")
    assert retrieved_trait.name == "Building"


def test_get_parent_traits():
    """Test retrieving parent traits from a domain."""
    domains = _validate_domains(DOMAINS_RESPONSE["data"])
    brick_domain = domains[2]
    trait = brick_domain.get_trait_by_id("brick:Air_Temperature_Sensor")
    parent_traits = get_parent_traits(trait, domains)
    expected_ids = {
        "brick:Air_Temperature_Sensor",
        "brick:Point",
        "brick:Sensor",
        "brick:Temperature_Sensor",
    }
    assert set(t.id for t in parent_traits) == expected_ids


def test_get_trait_by_id_exceptions():
    """Test error handling for get_trait_by_id."""
    domains = _validate_domains(DOMAINS_RESPONSE["data"])
    brick_domain = domains[2]

    # Test with non-existent ID
    with raises(KeyError):
        brick_domain.get_trait_by_id("non:existent:id")

    # Test with empty trait list
    empty_domain = _validate_domains(
        {
            "domainDefinitions": [
                {
                    "name": "Empty",
                    "prefix": "empty",
                    "description": "Empty domain",
                    "uri": "http://example.org/empty",
                    "traits": None,
                    "relationships": None,
                }
            ]
        }
    )[0]

    with raises(KeyError):
        empty_domain.get_trait_by_id("any:id")


def test_get_parent_traits_exceptions():
    """Test error handling for get_parent_traits."""
    domains = _validate_domains(DOMAINS_RESPONSE["data"])
    brick_domain = domains[2]

    # Test with non-existent parent IDs
    trait_no_parents = brick_domain.get_trait_by_id("brick:Point")
    parent_traits = get_parent_traits(trait_no_parents, domains)
    assert len(parent_traits) == 1
    assert parent_traits[0].id == "brick:Point"

    # Test with cyclic parent references
    cyclic_domain = _validate_domains(
        {
            "domainDefinitions": [
                {
                    "name": "Cyclic",
                    "prefix": "cyclic",
                    "description": "Cyclic domain",
                    "uri": "http://example.org/cyclic",
                    "traits": [
                        {
                            "name": "Trait1",
                            "id": "cyclic:trait1",
                            "parent_ids": [{"id": "cyclic:trait2"}],
                            "child_ids": [],
                            "equivalent_ids": [],
                            "domain_prefix": {"prefix": "cyclic"},
                        },
                        {
                            "name": "Trait2",
                            "id": "cyclic:trait2",
                            "parent_ids": [{"id": "cyclic:trait1"}],
                            "child_ids": [],
                            "equivalent_ids": [],
                            "domain_prefix": {"prefix": "cyclic"},
                        },
                    ],
                    "relationships": None,
                }
            ]
        }
    )[0]

    with raises(RecursionError):
        get_parent_traits(
            cyclic_domain.get_trait_by_id("cyclic:trait1"), [cyclic_domain]
        )

    # Test with None parent_ids
    trait_dict = {
        "name": "NoParents",
        "id": "test:no_parents",
        "parent_ids": None,
        "child_ids": [],
        "equivalent_ids": [],
        "domain_prefix": {"prefix": "test"},
    }
    no_parent_trait = Trait.model_validate(trait_dict)
    parent_traits = get_parent_traits(no_parent_trait, brick_domain)
    assert len(parent_traits) == 1
    assert parent_traits[0].id == "test:no_parents"


def test_get_trait_by_id_with_domains():
    """Test retrieving a trait by ID from lists of domains."""
    domains = _validate_domains(DOMAINS_RESPONSE["data"])
    trait = get_trait_by_id("brick:Building", domains)
    assert trait.name == "Building"

    # Test with non-existent ID across domains
    with raises(ValueError):
        get_trait_by_id("nonexistent:id", domains)

    # Test with empty domain list
    with raises(ValueError):
        get_trait_by_id("any:id", [])

    # Test with None domain list
    with raises(TypeError):
        get_trait_by_id("any:id", None)

    # Test with invalid domain data
    invalid_domains = [None, "not a domain", 123]
    with raises(AttributeError):
        get_trait_by_id("any:id", invalid_domains)
