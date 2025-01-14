from gql import Client, gql

from piscada_foresight.model import Domain, Trait


def get_domains(client: Client) -> list[Domain]:
    """Retrieve a list of all available domains.

    Parameters
    ----------
    client : Client
        The GQL client to use.

    Returns
    -------
    list[Domain]
        All available domains.
    """
    query = gql("""
query getDomains {
    domainDefinitions {
        name
        prefix
        description
        uri
        traits {
            name
            id
            parent_ids: parentTraits {
                id
            }
            child_ids: childTraits {
                id
            }
            equivalent_ids: equivalentTraits {
                id
            }
            domain_prefix: domain {
                prefix
            }
        }
        relationships {
            name
            id
            parent_ids: parentRelationships {
                id
            }
            child_ids: childRelationships {
                id
            }
            inverse_ids: inverse {
                id
            }
            domain_prefix: domain {
                prefix
            }
        }
    }
}
                """)
    response = client.execute(query)
    return _validate_domains(response)


def _validate_domains(response):
    """Validate and parse domain definitions from GraphQL response.

    Parameters
    ----------
    response : dict
        GraphQL response containing domain definitions

    Returns
    -------
    list[Domain]
        List of validated Domain objects
    """
    domains = []
    for domain_dict in response["domainDefinitions"]:
        domains.append(Domain.model_validate(domain_dict))
    return domains


def get_parent_traits(
    trait: Trait, domains: list[Domain], include_self: bool = True
) -> list[Trait]:
    """Gets all parent traits for a given trait recursively.

    Traverses up the trait hierarchy to collect all parent traits, optionally including
    the input trait itself.

    Parameters
    ----------
    trait : Trait
        The trait to get parents for.
    domains : list[Domain]
        List of domains containing the trait hierarchy.
    include_self : bool
        Whether to include the input trait in the result.

    Returns
    -------
    list[Trait]
        List of parent traits, ordered from most specific to most general.
    """
    parents = []
    if include_self:
        parents.append(trait)

    if trait.parent_ids:
        for parent_id in trait.parent_ids:
            parent = get_trait_by_id(parent_id, domains)
            parents.append(parent)
            if parent.parent_ids:
                parents.extend(get_parent_traits(parent, domains, include_self=False))

    return parents


def get_child_traits(
    trait: Trait, domain: Domain, include_self: bool = True
) -> list[Trait]:
    """Gets all child traits for a given trait recursively.

    Traverses down the trait hierarchy to collect all child traits, optionally including
    the input trait itself.

    Parameters
    ----------
    trait : Trait
        The trait to get children for.
    domain : Domain
        The domain containing the trait hierarchy.
    include_self : bool
        Whether to include the input trait in the result.

    Returns
    -------
    list[Trait]
        List of child traits, ordered from most general to most specific.
    """
    children = []
    if include_self:
        children.append(trait)

    if trait.child_ids:
        children.extend(
            [domain.get_trait_by_id(child_id) for child_id in trait.child_ids]
        )
        for child in children[1:]:
            if child.child_ids:
                children.extend(get_child_traits(child, domain, include_self=False))

    return children


def get_trait_by_id(trait_id: str, domains: list[Domain]) -> Trait:
    """Get a trait by its ID across all domains.

    Searches through all provided domains to find a trait matching the given ID.
    The trait ID must be in the format "domain:trait_name".

    Parameters
    ----------
    trait_id : str
        ID of the trait to find in "domain:trait_name" format
    domains : list[Domain]
        List of domains to search through

    Returns
    -------
    Trait
        The found trait

    Raises
    ------
    ValueError
        If the trait ID is not found in any domain or trait ID format is invalid
    """
    try:
        domain_prefix = trait_id.split(":")[0]
    except IndexError:
        raise ValueError(f"Invalid trait ID format: {trait_id}")

    for domain in domains:
        if domain.prefix == domain_prefix:
            try:
                return domain.get_trait_by_id(trait_id)
            except KeyError:
                break

    raise ValueError(
        f"Trait with ID '{trait_id}' not found in domain '{domain_prefix}'"
    )
