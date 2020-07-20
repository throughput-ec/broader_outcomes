'''

'''
from py2neo import Graph
from json import load

with open('.gitignore') as gi:
    good = False
    # This simply checks to see if you have a connection string in your repo.
    # I use `strip` to remove whitespace/newlines.
    for line in gi:
        if line.strip() == "connect_remote.json":
            good = True
            break

if good is False:
    print("The connect_remote.json file is not in your .gitignore file. \
           Please add it!")

with open('./connect_remote.json') as f:
    data = load(f)

graph = Graph(**data[1])

tx = graph.begin()

with open('./data/impact_terms.json') as f:
    triTerms = load(f)

check_index = """
  CALL db.indexes()
"""

indices = graph.run(check_index).data()

if len(indices) == 0:
    create_fulltext = """
    CALL db.index.fulltext.createNodeIndex("namesAndDescriptions",["OBJECT"],
    ["name", "description"])
    """
    add_index = graph.run(create_fulltext)

query_nodes = """
CALL db.index.fulltext.queryNodes("namesAndDescriptions", $insert)
  YIELD node, score
  WITH node, score
  MATCH (node:OBJECT)-[:isType]-(:TYPE {type:'schema:Grant'})
  MATCH (node)-[:Year_Started]-(year)
  OPTIONAL MATCH (node)-[:fundedBy]-(div)
  OPTIONAL MATCH (node)-[:Referenced_by]-(progref)
  OPTIONAL MATCH (node)-[:Funded_by]-(progfund)
  WITH node, COLLECT(div.name) AS division, year.Year as year,
    progref.Text AS reference,
    progfund.Text as funder, score
  WHERE ANY(x IN division WHERE x CONTAINS "Earth")
  RETURN DISTINCT node.AwardID AS award, node.name AS name,
    node.description AS description,
    COLLECT(DISTINCT year) AS year, division,
    COLLECT(reference) AS programReference,
    COLLECT(funder) AS programFund, score
  ORDER BY score
"""

for i in triTerms:
    insert = ' '.join(list(i.values())[0])
    query = graph.run(query_nodes, {'insert': insert}).data()
