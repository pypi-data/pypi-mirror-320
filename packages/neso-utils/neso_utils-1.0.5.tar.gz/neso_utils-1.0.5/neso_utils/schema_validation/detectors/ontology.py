# Functions that will be used to detect the data types from ontology files

from typing import Dict
from typing import List

from pandas import DataFrame

from rdflib import Graph

from .ddl import ONT_ALL_DTYPES_QUERY as all_dtypes_query
from .ddl import ONT_PRIMITIVE_DTYPES_QUERY as primitive_dtypes_query

from neso_utils.schema_validation.utils.pandas import convert_df_to_dict


class OntologyDatatypesHunter:
    """
    Class that will be used to detect the data types from ontology files.

    This class passes by the following steps:

    1. query the datatypes and stereotypes from the ontology, where the following datatypes specifications
    will be captured:
    - rdf:datatype: default for rdf data
    - stereotypes: when there's a specification of the types of the data

    and the on the second case, we want to filter out all the stereotypes that are not of the type Primitive.

    2. parse the SPARQL results - which will be a dictionary with the datatypes and stereotypes
    """

    def query_datatypes(self, ontology_graph: Graph) -> DataFrame:
        """
        Query all the datatypes and stereotypes from the ontology.

        There's two types of data type declarations that will be captured by this query:
        1. rdf:datatype: default for rdf data
        2. stereotypes: when there's a specification of the types of the data

        On the second case, we want to filter out all the stereotypes that are not of the type Primitive.

        Args:
            ontology_graph (Graph): The ontology graph.

        Returns:
            Dict: A dictionary with the data types.
        """

        records = [
            {
                "property": row.property.split("#")[-1],
                "datatype": row.dataType.split("#")[-1].lower(),
            }
            for row in ontology_graph.query(all_dtypes_query)
        ]

        return DataFrame(records)

    def get_primitive_dtypes(self, ontology_graph: Graph) -> List[str]:
        """
        From an ontology graph, this function will then obtain a list containing all the primitive datatypes.

        Args:
            ontology_graph (Graph): The ontology graph.

        Returns:
            List[str]: The list of primitive datatypes.
        """

        return list(
            set(
                [
                    row.datatype.split("#")[-1].lower()
                    for row in ontology_graph.query(primitive_dtypes_query)
                ]
            )
        )

    def conciliate_dtypes(self, df_dtypes: DataFrame) -> DataFrame:
        """
        Function that will be used to conciliate the datatypes from the ontology graph.

        There's datatypes that are defined on the ontologies that point out to other datatypes. In
        those cases, we need to conciliate the datatypes and make sure the datatype is pointing to
        the datatype that is on the base of the pyramide.

        _Example_:
        >>> df_dtypes = pd.DataFrame(data = [
                {'property': 'BaseVoltage.nominalVoltage', 'datatype': 'voltage'},
                {'property': 'Voltage.unit', 'datatype': 'unitsymbol'},
                {'property': 'Voltage.value', 'datatype': 'float'},
            ])
        >>> output = conciliate_dtypes(df_dtypes)
        >>> output
        >>> pd.DataFrame(data = [
                {'property': 'BaseVoltage.nominalVoltage', 'datatype': 'float'},
                {'property': 'Voltage.unit', 'datatype': 'unitsymbol'},
                {'property': 'Voltage.value', 'datatype': 'float'},
            ])

        This function will follow the following course of action:
        1. get only the ones that have a .value
        2. convert all the values from the property column to lower case
        3. apply a function to remove the .value from the property column
        4. iterate over the df_dtypes and update the datatype if property datatype is in df_value

        Args:
            df_dtypes (DataFrame): The datatypes dataframe.

        Returns:
            DataFrame: The conciliated datatypes dataframe.
        """

        df_value = df_dtypes[df_dtypes["property"].str.endswith(".value")].copy()
        df_value["property"] = (
            df_value["property"].str.lower().str.replace(".value", "", regex=False)
        )

        value_mapping = dict(zip(df_value["property"], df_value["datatype"]))

        df_dtypes["datatype"] = df_dtypes.apply(
            lambda row: value_mapping.get(row["datatype"], row["datatype"]), axis=1
        )

        return df_dtypes

    def filter_dtypes(
        self,
        df_dtypes: DataFrame,
        primitive_lst: List[str],
        target_col: str = "rdf_datatype",
    ) -> DataFrame:
        """
        Filter all the records from the obtained datatypes dataframe that are not primitive. Additionally,
        all the records that do not contain a stereotype will be kept - since these are the ones that are
        allusive to rdf:datatype.

        Args:
            df_dtypes (DataFrame): The datatypes dataframe.
            primitive_lst (List[str]): The list of primitive types.
            target_col (str): The column to filter the datatypes.

        Returns:
            DataFrame: The filtered datatypes dataframe.
        """

        return df_dtypes[df_dtypes[target_col].isin(primitive_lst)]

    def run(self, ontology_graph: Graph) -> Dict[str, str]:
        """
        Heart of operation. This function will be used to run the data types detection.

        By running this function, we will have the following results:
        - a dataframe, obtained from the ontology graph, containing all the datatypes that need to be
        held into account;
        - a list of primitive types - if there's any CIM stereotype that is of the type Primitive.
        - with the above, produce a dataframe that will be a map for the injection of the datatypes.

        This function will follow the following course of action:
        1. query the datatypes from the ontology graph
        2. get the primitive datatypes
        3. conciliate the datatypes - since there's some datatypes that are defined on the ontologies
        that point out to other datatypes
        4. filter out all the records that are not primitive
        5. filter out all the records that end with .value
        6. convert the dataframe to a dictionary

        Args:
            ontology_graph (Graph): The ontology graph.

        Returns:
            Dict[str, str]: A dictionary with the datatypes and stereotypes.
        """

        df_ont = self.query_datatypes(ontology_graph)
        primitive_lst = self.get_primitive_dtypes(ontology_graph)
        df_ont = self.conciliate_dtypes(df_ont)
        df_dtypes = self.filter_dtypes(df_ont, primitive_lst, "datatype")
        df_dtypes = df_dtypes[~df_dtypes["property"].str.endswith(".value")]

        return convert_df_to_dict(df_dtypes, "property", "datatype")
