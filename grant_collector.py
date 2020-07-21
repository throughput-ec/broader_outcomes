'''
Detect grants with broader outcomes.

This script selects grants from the NSF using a set of name and abstract terms
and returns an object containing the matching terms, award numbers, year of
the award, and some other terms.
'''

from py2neo import Graph
from json import load
import copy
from fuzzywuzzy import fuzz


def unlist(x):
    """Simplify a list of lists to a list of depth 1.

    Parameters
    ----------
    x : list
        A list object, may be a vector or a list of lists.

    Returns
    -------
    list
        A list of depth = 1.  Does not subset strings (as opposed to the
        `itertools` version).

    """
    if not all(map(lambda y: type(x) is list, x)):
        return x
    else:
        outlist = []
        for i in x:
            if type(i) is list:
                i = unlist(i)
                for j in i:
                    outlist.append(j)
            else:
                outlist.append(i)
    return outlist


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
    ["name", "description"], { analyzer: "english",
    eventually_consistent: "true" })
    """
    add_index = graph.run(create_fulltext)

query_nodes = """
  MATCH (node:OBJECT)-[:isType]-(:TYPE {type:'schema:Grant'})
  WHERE tolower(node.description) CONTAINS tolower($insert)
  MATCH (node)-[:Year_Started]-(year)
  OPTIONAL MATCH (node)-[:fundedBy]-(div)
  OPTIONAL MATCH (node)-[:Referenced_by]-(progref)
  OPTIONAL MATCH (node)-[:Funded_by]-(progfund)
  WITH node, COLLECT(div.name) AS division, year.Year as year,
    progref.Text AS reference,
    progfund.Text as funder
  WHERE ANY(x IN division WHERE x CONTAINS "Earth")
  RETURN DISTINCT node.AwardID AS award, node.name AS name,
    node.description AS description,
    COLLECT(DISTINCT year) AS year, division,
    COLLECT(reference) AS programReference,
    COLLECT(funder) AS programFund,
    $insert AS term
"""

# Create the list of grants:
bodb = []

allterms = set()

for i in triTerms:
    terms = list(i.values())[0]
    for j in terms:
        allterms.add(j)

for i in allterms:
    print(i)
    bodb.append(graph.run(query_nodes, {'insert': i}).data())

termdict = {}

for i in range(len(allterms) - 1):
    termdict[list(allterms)[i]] = len(bodb[i])

flatList = []
awardid = []

for i in bodb:
    for j in i:
        toadd = copy.deepcopy(j)
        toadd['term'] = [toadd['term']]
        for k in ['division', 'programReference',
                  'programFund', 'division']:
            if any(list(map(lambda x: type(x) is list, toadd[k]))):
                vector = unlist(toadd[k])
            else:
                vector = toadd[k]
            toadd[k] = list(set(map(lambda x: x.lower(), vector)))
        if not toadd['award'] in awardid:
            flatList.append(toadd)
            awardid.append(toadd['award'])
            print(len(awardid))
        else:
            print('.', end='')
            for x in flatList:
                if toadd['award'] == x['award']:
                    x['term'].append(toadd['term'])
                    x['term'] = unlist(x['term'])
                    break

# Now we have flatList, which is a set of grants that have some or all of
# the search terms.  We want to try to group
groupTitle = []
yearName = []

for i in flatList:
    tester = copy.deepcopy(i)
    tester['award'] = [tester['award']]
    match = 0
    for j in groupTitle:
        if j['year'] == tester['year']:
            ratio = fuzz.token_sort_ratio(j['name'].lower(),
                                          tester['name'].lower())
            ratiotwo = fuzz.token_sort_ratio(j['description'].lower(),
                                             tester['description'].lower())
            if ratio > 90 and ratio < 100:
                print([ratio,
                       ratiotwo, j['name'].lower(),
                       tester['name'].lower()])
            if ratio > 90:
                [j['award']].append(tester['award'])
                j['award'] = unlist(j['award'])
                match = 1
                print('.', end='')
                break
    if match == 0:
        groupTitle.append(tester)
        print(len(groupTitle))
