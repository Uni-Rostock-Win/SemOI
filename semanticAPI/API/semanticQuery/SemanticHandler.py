import rdflib
import re
from SPARQLWrapper import SPARQLWrapper, JSON
class SemanticHandler():
    
    
    def __init__(self):
        self.rdf = rdflib.Graph()
        self.rdf.parse(location='rdf.ttl', format="turtle")

    @staticmethod
    def scene2Array(json):
        firstIteration = True
        array = []
        tmpArray = []
        scenes = []
        actualOccasion = ""
        counter = 0
        for jsonObject in json:
            counter += 1
            if(actualOccasion != jsonObject["occasion"] or len(json) == counter):
                print("bum")
                tmpArray.append({"objectName": jsonObject["objectName"]})
                tmpArray.append({"imageClassifier": jsonObject["imageClassifier"]})
                actualOccasion = jsonObject["occasion"]
                tmpArray.append({"occasion": actualOccasion})
                if(len(json) != counter):
                    scenes = []
                scenes.append(jsonObject["scene"])
                if(not(firstIteration)):
                    print(scenes)
                    tmpArray.append({"scenes": scenes})
                    array.append(tmpArray)
            else:
                scenes.append(jsonObject["scene"])
            firstIteration = False
        return array

    def getSemanticEnhancement(self, filterId):
        sparql =    SPARQLWrapper("http://SemanticServer/imageRecog/sparql")
        if filterId != ("" or None):
            filter =   'FILTER(str(?classifier) = "' + filterId + '")'
        else:
            filter = ""
        queryBuilder = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX win: <http://wirtschaftsinformatik.uni-rostock.de/studentimagerecog#>
        PREFIX sema: <http://sema.informatik.uni-rostock.de/sema#>
        SELECT ?subject ?classifier ?occasion ?scene
        WHERE { 
        ?subject rdfs:subClassOf win:DetectedClasses .
        ?subject win:ImageClassifier ?classifier . 
        ?subject rdfs:subClassOf [
        owl:onProperty sema:hasOccasion ;
        owl:someValuesFrom ?occasion ]
        .
        ?scene rdfs:subClassOf [
        owl:onProperty sema:hasOccasion ;
	    owl:someValuesFrom ?occasion]
        """ + filter + "} "
        print(queryBuilder)
        #qres = self.rdf.query(queryBuilder)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(queryBuilder)
        qres = sparql.queryAndConvert()
        responseBuilder  = []
        
        for row in qres["results"]["bindings"]:
            responseBuilder.append({"objectName": re.sub("((.*)#)", "",row["subject"]["value"]),
            "imageClassifier": row["classifier"]["value"],
            "occasion":  re.sub("((.*)#)", "", row["occasion"]["value"]),
            "scene": re.sub("((.*)#)", "", row["scene"]["value"])})
            # responseBuilder.append({"objectName": row["subject"]["value"],
            # "imageClassifier": row["classifier"]["value"],
            # "occasion":   row["occasion"]["value"],
            # "scene": row["scene"]["value"]})
        return self.scene2Array(responseBuilder)
  

    
    
    