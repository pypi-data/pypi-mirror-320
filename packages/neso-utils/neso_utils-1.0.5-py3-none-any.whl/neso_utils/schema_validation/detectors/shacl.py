# Functions that will be used to detect the data types from ontology files

from pandas import DataFrame

from rdflib import Graph

from .ddl import SHACL_ALL_DTYPES_QUERY as dtypes_query


def shacl_datatypes_hunter(shacl_graph: Graph) -> DataFrame:
    """
    Query all the datatypes from the set of rules provided by the SHACL graph.

    There's two types of data type declarations that will be captured by this query:
    1. rdf:datatype: default for rdf data
    2. stereotypes: when there's a specification of the types of the data

    On the second case, we want to filter out all the stereotypes that are not of the type Primitive.

    Args:
        shacl_graph (Graph): The shacl graph.

    Returns:
        Dict: A dictionary with the data types.
    """

    records = [
        {
            "property": str(row.property).split("#")[-1],
            "datatype": str(row.datatype).split("#")[-1],
        }
        for row in shacl_graph.query(dtypes_query)
    ]

    return DataFrame(records)
