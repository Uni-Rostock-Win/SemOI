import rdflib
import re

class SemanticHandler():
    
    
    def __init__(self):
        self.rdf = rdflib.Graph()
        self.rdf.parse(location='rdf.ttl', format="turtle")

    

    def getSemanticEnhancement(self, filterId):
        
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
        SELECT ?subject ?classifier ?occasion 
        WHERE { ?subject rdfs:subClassOf win:DetectedClasses .
        ?subject win:ImageClassifier ?classifier . 
        ?subject rdfs:subClassOf [
        owl:onProperty sema:hasOccasion ;
        owl:someValuesFrom ?occasion ]
        .
        """ + filter + "}"
        print(queryBuilder)
        qres = self.rdf.query(queryBuilder)
        responseBuilder  = []
        for row in qres:
            responseBuilder.append({"objectName": re.sub("((.*)#)", "",row[0]),
            "imageClassifier": row[1],
            "occasion":  re.sub("((.*)#)", "", row[2])})
        return responseBuilder
  

    
    
   # getSemanticEnhancement(rdf, "/m/07k1x") 
   
    