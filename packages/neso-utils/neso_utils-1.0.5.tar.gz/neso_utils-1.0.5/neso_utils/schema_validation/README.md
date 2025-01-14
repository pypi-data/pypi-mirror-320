<h1 align='center'>
    <strong> Schema Validation </strong>
</h1>

<p align='center'>
    Validate your rdf data against an ontology and SHACL files - even when the data lacks datatypes definition.
</p>


<div align="center">

  <a href="code coverage">![coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)</a>
  <a href="tests">![tests](https://img.shields.io/badge/tests-62%20passed%2C%200%20failed-brightgreen)</a>
  <a href="python version">![sbt_version](https://img.shields.io/badge/python-3.10-blue?logo=python&logoColor=white)</a>

</div>

## **1. Intro**

Sometimes rdf data might lack datatypes definition. Under these circumstances, w3c states that whenever no datatype is specified, the data is by default considered Literal (the equivalente of a string).

These can be tricky, if you want to validate your data against a set of ontologies and SHACL files, especially when you can't configure the source system to add the datatypes.

This is where the Schema Validation comes in. It will inject the datatypes into your data and then validate it against the ontologies and SHACL files.

## **2. How to Use - _high level_**

```python
from neso_utils import SchemaCertifier

from neso_utils.schema_validation import InferenceType
from neso_utils.schema_validation import CIMInstanceTypes

... assuming that you have ontologies, SHACL and data ready to be used...

validation_result = SchemaCertifier(
    data_graph=data_graph,
    shacl_graph=shacl_graph,
    ont_graph=ont_graph,
    inference_type=InferenceType.BOTH,
    cim_instance=CIMInstanceTypes.EQ,
    store_data=True
).run()
```

## **3. How it works under the hood**

This solution divides itself into three main parts:
- The **_Datatypes Hunter_**: This is the module that will be responsible for extracting the datatypes from the ontologies.
- The **_Datatypes Injector_**: This is the module that will be responsible for injecting the datatypes into the data.
- The **_Validator_**: This is the module that will be responsible for validating the data against the ontologies and SHACL files.

Let's dive into each one of them.

### **3.1. Datatypes Hunter**

As stated before, the datatypes hunter is the module that will be responsible for extracting the datatypes from the ontologies.

Additionally, it's important to retain something about it's implementation. We have an hunter that is fully dedicated for the ontologies, and another one for the SHACL files.

This is because the ontologies and the SHACL files have different structures, and therefore, different strategies to extract the datatypes.

### **3.2. Datatypes Injector**

This module - that is essentially conposed of a single function - will be responsible for injecting the datatypes into the data.

### **3.3. Validator**

Last but not least, the validator script contains the SchemaCertifier class. This class is the one that will be responsible for the validation of the data.

Going back to module mentioned (Datatypes Hunter), this module will be responsible for concialiating the outcomes of the hunters (if the user provides both ontologies and SHACL files).

By default, the SHACLs are more assertive when it comes to datatypes definition, and therefore, the datatypes hunter for the SHACLs will be the one responsible for dictating the final datatypes.

This module leverages the pyshacl to perform the validation.

The user can choose the specs that will be leveraged on the validation process.