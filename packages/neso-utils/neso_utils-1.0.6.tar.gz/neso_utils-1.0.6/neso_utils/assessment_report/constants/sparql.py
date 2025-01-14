# constants for the sparql queries

DEFAULT_QUERY_ENDPOINT = "https://eso.data-spikes.labs.mesh-ai.com/api/sparql/knowledge/sparql"
DEFAULT_QUERY = """
SELECT ?s ?p ?o
WHERE {
  ?s ?p ?o.
}
ORDER BY DESC(?date)
LIMIT 5
"""
