'''
This takes the awards in the output award list and then adds the authors from
the NSF Award Database.
'''

from py2neo import Graph
from json import load, loads
import csv


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


def cleanlist(x):
    out = x.split(',')
    out = map(lambda x: x.strip(), out)
    return(list(out))


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

grants = []

with open('./data/output/awards.csv') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        grants.append(row)

for row in grants:
    if len(row) == 10:
        query = """
            MATCH (:TYPE {type:'schema:Grant'})<-[:isType]-(n:OBJECT)<-[:hasGrant]-(a:AGENT)-[:affiliatedWith]->(in:Institution)
            WHERE n.AwardID IN $awards
            RETURN DISTINCT a.name AS name,
                            a.email AS email,
                            COLLECT(in.name) AS institution
            """
        row.append(graph.run(query,
                             {'awards': loads(row[0].replace("'", '"'))}).data())
        print('.', end='')
    else:
        print('skip')

header.append('recipients')

# Now open the old award file and remove lines that have been dropped
# before, and flag lines that have already been checked by Amy:
clean = []

with open('./data/input/award_fileClean.csv') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        clean.append(row)

dirty = []

with open('./data/input/award_file.csv') as file:
    reader = csv.reader(file)
    header = next(reader)
    for row in reader:
        dirty.append(row)

for nrows in grants:
    awd = loads(nrows[0].replace("'", '"'))
    checked = False
    for rows in clean:
        awdClean = cleanlist(rows[2])
        if any(item in awdClean for item in awd):
            checked = True
            nrows.append('good')
            break
    if checked is False:
        unclean = False
        for drows in dirty:
            awdDirty = cleanlist(drows[2])
            if any(item in awd for item in awdDirty):
                unclean = True
                nrows.append('bad')
                break
    if unclean is False:
        nrows.append('unchecked')

for x in grants[:]:
    if len(x) == 12 and x[11] == 'bad':
        grants.remove(x)

header = ['awardid', 'title', 'description',
          'year', 'division', 'program',
          'matched terms',
          'termcount', 'awardcount', 'recipients', 'checked']

with open('./data/output/awards.csv', 'w', newline='') as f:
    writer = csv.writer(f,
                        delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    for d in grants:
        if any(2015 < int(item) for item in loads(d[3])):
            writer.writerow(d)
