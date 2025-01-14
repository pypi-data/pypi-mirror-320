---
title: README
author: Jan-Michael Rye
---

# Synopsis

A light wrapper around [SPARQLWrapper](https://pypi.org/project/SPARQLWrapper/) for [Wikidata's SPARQL query service](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service). The wrapper attempts to follow Wikidata's usage policy regarding user-agent strings and query frequency.

The wrapper also wraps expected exceptions in a custom exception class to facilitate error handling.


## Links

[insert: links 2]: #

### GitLab

* [Homepage](https://gitlab.inria.fr/jrye/wikidata-sparqlwrapper)
* [Source](https://gitlab.inria.fr/jrye/wikidata-sparqlwrapper.git)
* [Documentation](https://jrye.gitlabpages.inria.fr/wikidata-sparqlwrapper)
* [Issues](https://gitlab.inria.fr/jrye/wikidata-sparqlwrapper/-/issues)
* [GitLab package registry](https://gitlab.inria.fr/jrye/wikidata-sparqlwrapper/-/packages)

### Other Repositories

* [Python Package Index](https://pypi.org/project/wikidata-sparqlwrapper/)

[/insert: links 2]: #

# Usage

~~~python
from wikidata_sparqlwrapper import (
    WikidataSPARQLWrapper,
    WikidataSPARQLWrapperError,
    construct_user_agent_string,
)

# Construct a user-agent string that uniquely identifies your code and which
# includes a contact email address.
agent = construct_user_agent_string(name="MyApp", email="my_email@example.com")

# Instantiate the Wikidata SPARQL wrapper.
wrapper = WikidataSPARQLWrapper(user_agent=agent)

# Construct a SPARQL query.
query = """\
SELECT ?item ?itemLabel
WHERE
{
    ?item wdt:P31 wd:Q146.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

# Get the SPARQLWrapper query object directly. The format will be set to JSON.
# This example includes error handling but it is not necessary here. The user
# may catch the error elsewhere such as in the main function.
try:
    response = wrapper.query(query)
except WikidataSPARQLWrapperError as err:
    # Handle the error here.

# Get the bindings directly. The remarks about error handling from above apply
# here too.
try:
    bindings = wrapper.query_bindings(query)
except WikidataSPARQLWrapperError as err:
    # Handle the error here.

# Do something with the bindings.
for binding in bindings:
    print(binding["itemLabel"]["value"])
~~~
