from SPARQLWrapper import SPARQLWrapper, JSON

# Initialize the SPARQLWrapper with the endpoint URL
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

# Define the SPARQL query
sparql_query = """
SELECT ?country ?countryLabel ?capital ?capitalLabel WHERE {
  ?country wdt:P31 wd:Q3624078;  # instances of sovereign states
           wdt:P36 ?capital.    # has capital
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
LIMIT 10
"""

# Set the query and the return format (JSON)
sparql.setQuery(sparql_query)
sparql.setReturnFormat(JSON)

# Perform the query and convert the result to a Python dictionary
results = sparql.query().convert()

# Iterate through the results and print them out
for result in results["results"]["bindings"]:
    country = result["countryLabel"]["value"]
    capital = result["capitalLabel"]["value"]
    print(f"Country: {country}, Capital: {capital}")
