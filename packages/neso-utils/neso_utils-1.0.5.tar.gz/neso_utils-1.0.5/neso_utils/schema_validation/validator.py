# Functions that will be used to validate the data agains both the SHACL and ontology files

import os

import pandas as pd

from rdflib import Graph
from rdflib import Namespace

from enum import Enum

from pyshacl import validate

from typing import Dict
from typing import Optional

from dataclasses import dataclass

from xml.etree.ElementTree import tostring
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ElementTree

from neso_utils.schema_validation.injector import rdf_dtype_injector
from neso_utils.schema_validation.utils.pandas import dfs_conciliator

from neso_utils.schema_validation.detectors.ontology import OntologyDatatypesHunter
from neso_utils.schema_validation.detectors.shacl import shacl_datatypes_hunter


@dataclass
class InferenceType(Enum):
    ONTOLOGY = "ontology"
    SHACL = "shacl"
    BOTH = "both"


@dataclass
class CIMInstanceTypes(Enum):
    EQ = "eq"
    SSH = "ssh"
    EQBD = "eqbd"
    DL = "dl"
    NONE = "none"


class SchemaCertifier:
    """
    Class that will be used to certify the schema of data based on the ontology and SHACL files.

    This class - and a decent part of its arguments - will be used to configure the validation module
    that will be used to validate the schema of the data against the ontology and SHACL files. This
    module is part of the pyshacl library.

    Additionally, it's important to bear in mind that when a SHACL file is provided this will have
    the priority over the ontology file.
    This means that:
    1. whenever a datatype haven't been captured by the ontology file, the datatypes from the SHACL file
    will be added to the list of datatypes to be injected into the data graph;
    2. whenever a datatype is captured by both the ontology and SHACL files, the datatype from the SHACL file
    will be used.

    Args:
        data_graph: Graph, the data graph to be certified
        shacl_graph (Optional, Graph): Graph, the SHACL graph to be used for the certification
        ont_graph (Optional, Graph): Graph, the ontology graph to be used for the certification
        abort_on_first (Optional, boolean): Whether to abort the validation on the first violation
        allow_infos (Optional, boolean): Whether to allow infos in the validation
        allow_warnings (Optional, boolean): Whether to allow warnings in the validation
        inference (Optional, str): The inference type to be used for the validation
        inplace (Optional, boolean): Whether to perform the validation in place
        max_validation_depth (Optional, int): The maximum validation depth
        meta_shacl (Optional, bool): Whether to use the meta-shacl rules
        advanced (Optional, bool): Whether to use the advanced validation rules
        js (Optional, bool): Whether to use the js validation rules
        debug (Optional, bool): Whether to use the debug mode
        inference_type (Optional, InferenceType): The inference type to be used for the validation
        store_data (Optional, boolean): Whether to store the data after the injection in the server
    """

    def __init__(
        self,
        data_graph: Graph,
        shacl_graph: Optional[Graph] = None,
        ont_graph: Optional[Graph] = None,
        abort_on_first: Optional[bool] = False,
        allow_infos: Optional[bool] = False,
        allow_warnings: Optional[bool] = False,
        inference: Optional[str] = "none",
        inplace: Optional[bool] = False,
        max_validation_depth: Optional[int] = None,
        meta_shacl: Optional[bool] = False,
        advanced: Optional[bool] = True,
        js: Optional[bool] = False,
        debug: Optional[bool] = False,
        inference_type: Optional[InferenceType] = InferenceType.ONTOLOGY,
        cim_instance: Optional[CIMInstanceTypes] = None,
        store_data: Optional[bool] = False,
    ):
        self.data_graph = data_graph
        self.shacl_graph = shacl_graph
        self.ont_graph = ont_graph

        self._abort_on_first = abort_on_first
        self._allow_infos = allow_infos
        self._allow_warnings = allow_warnings
        self._inference = inference
        self._inplace = inplace
        self._max_validation_depth = max_validation_depth
        self._meta_shacl = meta_shacl
        self._advanced = advanced
        self._js = js
        self._debug = debug

        self._inference_type = inference_type
        self._store_data = store_data
        self._cim_instance = cim_instance

    @property
    def abort_on_first(self) -> bool:
        return self._abort_on_first

    @property
    def allow_infos(self) -> bool:
        return self._allow_infos

    @property
    def allow_warnings(self) -> bool:
        return self._allow_warnings

    @property
    def inference(self) -> Optional[str]:
        return self._inference

    @property
    def inplace(self) -> bool:
        return self._inplace

    @property
    def max_validation_depth(self) -> Optional[int]:
        return self._max_validation_depth

    @property
    def meta_shacl(self) -> Optional[bool]:
        return self._meta_shacl

    @property
    def advanced(self) -> Optional[bool]:
        return self._advanced

    @property
    def js(self) -> Optional[bool]:
        return self._js

    @property
    def debug(self) -> Optional[bool]:
        return self._debug

    @property
    def store_data(self) -> Optional[bool]:
        return self._store_data

    @property
    def inference_type(self) -> InferenceType:
        return self._inference_type

    @property
    def cim_instance(self) -> CIMInstanceTypes:
        return self._cim_instance

    def _get_datatypes(self) -> Dict[str, str]:
        """
        Handler that will return the list of datatypes depending on the inference type
        chosen.
        """

        match self.inference_type:
            case InferenceType.ONTOLOGY:
                return OntologyDatatypesHunter().run(self.ont_graph)

            case InferenceType.SHACL:
                return shacl_datatypes_hunter(self.shacl_graph)

            case InferenceType.BOTH:
                ont_dtypes = pd.DataFrame(OntologyDatatypesHunter().run(self.ont_graph))
                shacl_dtypes = pd.DataFrame(shacl_datatypes_hunter(self.shacl_graph))

                return dfs_conciliator(
                    ont_dtypes, shacl_dtypes, "property", "datatype"
                ).to_dict(orient="records")

    def _store_injected_data(self, data: Graph):
        """
        Stores the data graph with the datatypes injected.
        """

        outputs_dir = "./injected_samples"
        os.makedirs(outputs_dir, exist_ok=True)

        eq_landing_path = os.path.join(
            outputs_dir, f"{self.cim_instance.value}_datatypes_injected.xml"
        )
        data_tree = ElementTree(data)
        data_tree.write(eq_landing_path, encoding="utf-8", xml_declaration=True)

        return eq_landing_path

    def failure_report(self, raw_data: str, results_graph: Graph) -> Dict[str, str]:
        """
        Build an error report from the data obtained by the validation from pyshacl library.

        _Error Report Shape_:
        {
            'error_rate': 123,
            'errors': [
                'error_1',
                'error_2',
                'error_3',
            ],
            'raw_data': 'data_graph_as_xml'
        }

        Args:
            raw_data (str): raw version of the data submitted for validation process
            results_graph (Graph): The graph containing the validation results

        Returns:
            Dict[str, str]: A dictionary containing the error report
        """

        SH = Namespace("http://www.w3.org/ns/shacl#")

        errors_lst = [
            {
                "focus_node": results_graph.value(
                    subject=result, predicate=SH.focusNode
                ),
                "source_constraint": results_graph.value(
                    subject=result, predicate=SH.sourceConstraintComponent
                ),
                "value": results_graph.value(subject=result, predicate=SH.value),
                "message": results_graph.value(
                    subject=result, predicate=SH.resultMessage
                ),
            }
            for result in results_graph.subjects(
                predicate=SH.resultSeverity, object=SH.Violation
            )
        ]

        number_of_violations = len(
            list(results_graph.triples((None, SH.resultSeverity, SH.Violation)))
        )

        return {
            "error_rate": number_of_violations,
            "errors": errors_lst,
            "raw_data": raw_data,
        }

    def run(self) -> None:
        """
        Heart of the operation.

        This function will not only be responsible for calling out the validation but also
        all the required operations to get the datatypes and the data ready for evaluation.
        """

        # get the datatypes
        datatypes = self._get_datatypes()

        # convert the data graph to rdf/xml
        data = fromstring(self.data_graph.serialize(format="xml"))

        # inject the datatypes
        data = rdf_dtype_injector(data, datatypes)

        # store the data graph
        data_path = self._store_injected_data(data)

        # convert back to rdf graph
        data_graph = Graph()
        data_graph.parse(data_path, format="xml")

        if not self.store_data:
            os.remove(data_path)

        # else call the validate method directly
        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=self.shacl_graph,
            ont_graph=self.ont_graph,
            inference=self.inference,
            abort_on_first=self.abort_on_first,
            allow_infos=self.allow_infos,
            allow_warnings=self.allow_warnings,
            meta_shacl=self.meta_shacl,
            advanced=self.advanced,
            js=self.js,
            debug=self.debug,
        )

        if not conforms:
            return self.failure_report(tostring(data), results_graph)

        return True
