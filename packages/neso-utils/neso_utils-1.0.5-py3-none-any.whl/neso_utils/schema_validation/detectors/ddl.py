# Definition of constants that will be used by the schema validation module

ONT_PRIMITIVE_DTYPES_QUERY = """
PREFIX cims: <http://iec.ch/TC57/1999/rdf-schema-extensions-19990926#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX dl: <http://iec.ch/TC57/ns/CIM/DiagramLayout-EU#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?datatype ?label ?comment ?definition ?package
WHERE {
  {
    # Capture datatypes explicitly marked as Primitive (using cims:stereotype)
    ?datatype cims:stereotype "Primitive" .
    OPTIONAL { ?datatype rdfs:label ?label . }
    OPTIONAL { ?datatype rdfs:comment ?comment . }
  }
  UNION
  {
    # Capture datatypes from rdfs:range, filtered for xsd datatypes
    ?property rdfs:range ?datatype .
    FILTER(STRSTARTS(STR(?datatype), "http://www.w3.org/2001/XMLSchema#"))
    OPTIONAL { ?datatype rdfs:label ?label . }
    OPTIONAL { ?datatype rdfs:comment ?comment . }
  }
  UNION
  {
    # Capture datatypes marked with dl:isPrimitive
    ?datatype dl:isPrimitive "True" .
    OPTIONAL { ?datatype rdfs:label ?label . }
    OPTIONAL { ?datatype skos:definition ?definition . }
    OPTIONAL { ?datatype dl:Package ?package . }
  }
}
"""

ONT_ALL_DTYPES_QUERY = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cims: <http://iec.ch/TC57/1999/rdf-schema-extensions-19990926#>
PREFIX cim: <http://iec.ch/TC57/NonStandard/UML#>

SELECT ?property ?dataType ?stereotype
WHERE {
  {
    ?property rdfs:range ?dataType .
    OPTIONAL {
      ?dataType cims:stereotype ?stereotype .
    }
  }
  UNION
  {
    ?property cims:dataType ?dataType .
    OPTIONAL {
      ?dataType cims:stereotype ?stereotype .
    }
  }
  UNION
  {
    ?property cim:dataType ?dataType .
    OPTIONAL {
      ?dataType cim:stereotype ?stereotype .
    }
  }
}
"""

SHACL_ALL_DTYPES_QUERY = """
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT DISTINCT ?property ?datatype
WHERE {
  {
    # Case 1: Nested under a shape
    ?shape sh:property ?propertyShape .
    ?propertyShape sh:path ?property ;
                   sh:datatype ?datatype .
  }
  UNION
  {
    # Case 2: Standalone PropertyShape
    ?propertyShape rdf:type sh:PropertyShape ;
                   sh:path ?property ;
                   sh:datatype ?datatype .
  }
}
"""
