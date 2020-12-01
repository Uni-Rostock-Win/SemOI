import json, csv
import rdflib
from rdflib.namespace import RDF, OWL, RDFS

def label2name(label):
    for item in csvData:
        if(item[0] == label):
            return item[1]

def iter (earlierItem, g, jsonO):
    counter = 0
    currentItem = earlierItem  
    for item in jsonO:
        if(currentItem == None):
            earlierItem = "DetectedClasses"
            currentItem = earlierItem
        elif(item == "Subcategory"):
            print("recursion")
            earlierItem = currentItem
            iter(currentItem, g,jsonO[item])
        elif(item == "LabelName" and counter != None):
            print(jsonO)
            currentItem = label2name(jsonO[item])
            print("add: " + currentItem)
            g.add((
                rdflib.URIRef(baseUri + currentItem.replace(" ", "")),
                RDFS.subClassOf,
                rdflib.URIRef(baseUri + earlierItem.replace(" ", ""))
            ))
            g.add((
                rdflib.URIRef(baseUri + currentItem.replace(" ", "")),
                rdflib.URIRef(baseUri + "ImageClassifier"),
                rdflib.Literal(jsonO[item])
            ))
            continue
        elif(item == "Part"):
            currentItem = "Part"
        else:
            # Unwrap
            if(currentItem != "Part"):
                iter(earlierItem, g, jsonO[counter])
        counter += 1




with open('bbox_labels_600_hierarchy.json') as myFile:
    data = myFile.read()
jsonObj = json.loads(data)

csvData = []
with open('labelDescription.csv', encoding="utf8") as csvFile:
    csvReader = csv.reader(csvFile, delimiter=';')
    for row in csvReader:
        csvData.append(row)

print(csvData[1][1])

baseUri =  ("http://wirtschaftsinformatik.uni-rostock.de/studentImageRecog#")

g = rdflib.Graph()

iter(None, g, jsonObj)

ontology = g.serialize(format="turtle").decode("utf-8")

with open("rdfTarget.rdf", "w") as rdfOutput:
    rdfOutput.write(ontology)

#print(g.serialize(format="turtle").decode("utf-8"))

