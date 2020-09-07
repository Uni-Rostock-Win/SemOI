import rdflib
import re
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
class SemanticHandler():
    
    
    def __init__(self):
        # self.rdf = rdflib.Graph()
        # self.rdf.parse(location='rdf.ttl', format="turtle")
        pass

    @staticmethod
    def scene2Array(json):
        scenes = []
        array = []
        scenes = []
        firstElement = True
        
        for jsonObject in json:
            if(firstElement):
                array.append({"objectName": jsonObject["objectName"]})
                array.append({"imageClassifier": jsonObject["imageClassifier"]})
                firstElement = False
            scenes.append(jsonObject["scene"])
        array.append({"scenes": scenes})
        print(array)
        return array

    def getSemanticEnhancement(self, filterId):
        sparql = SPARQLWrapper("http://semanticserver:3030/ImageRecog")
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials("admin", "stud123")
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
        SELECT DISTINCT ?subject ?classifier ?scene
        WHERE { 
        ?subject rdfs:subClassOf+ win:DetectedClasses .
        ?subject win:ImageClassifier ?classifier . 
        {
            ?subject rdfs:subClassOf [
            owl:onProperty sema:hasOccasion ;
            owl:someValuesFrom ?occasion ]
            .
            ?scene rdfs:subClassOf [
            owl:onProperty sema:hasOccasion ;
	        owl:someValuesFrom ?occasion]
        }
        UNION
        {
            ?subject rdfs:subClassOf [
                owl:onProperty sema:hasEnvironment ;
                owl:someValuesFrom ?scene
            ]
        }
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
         #   "occasion":  re.sub("((.*)#)", "", row["occasion"]["value"]),
            "scene": re.sub("((.*)#)", "", row["scene"]["value"])})
            # responseBuilder.append({"objectName": row["subject"]["value"],
            # "imageClassifier": row["classifier"]["value"],
            # "occasion":   row["occasion"]["value"],
            # "scene": row["scene"]["value"]})
        return self.scene2Array(responseBuilder)
  

    
    
    