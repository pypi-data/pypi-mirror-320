# utilities functions around sparql

import requests

from typing import Dict

from neso_utils.assessment_report.constants.sparql import DEFAULT_QUERY
from neso_utils.assessment_report.constants.sparql import DEFAULT_QUERY_ENDPOINT


def run_sparql_query(
    secret: str, query: str = DEFAULT_QUERY, endpoint: str = DEFAULT_QUERY_ENDPOINT
) -> Dict:
    """
    Perform a SPARQL query on the given endpoint and returns the response.

    Args:
        secret (str): The cookie secret to use for authentication.
        query (str): The SPARQL query to run.
        endpoint (str): The endpoint to run the query on.

    Returns:
        dict: The response from the SPARQL query.
    """

    headers = {
        "cookie": f"_oauth2_proxy={secret}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    payload = {
        "query": query,
    }
    response = requests.post(endpoint, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()["results"]["bindings"]
    else:
        print(f"Error: {response.status_code} - {response.text}")
