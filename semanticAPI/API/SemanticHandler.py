import re, os, rdflib, logging


class SemanticHandler():
    
    
    def __init__(self):
        self.rdf = rdflib.Graph(store="OxMemory")
        self.rdf.parse(location="ontologies/rdf.owl", format="application/rdf+xml")
        

    @staticmethod
    def scene2Array(json):
        scenes = []
        array = []
        scenes = []
        firstElement =False 
        
        for jsonObject in json:
            if(firstElement):
                array.append({"objectName": jsonObject["objectName"]})
                array.append({"imageClassifier": jsonObject["imageClassifier"]})
                firstElement = False
            scenes.append(jsonObject["scene"])
        array.append({"scenes": scenes})
        print(array)
        return array

    def getSemanticEnhancement(self, detectorIds: list):
        filter =   'FILTER(str(?classifier) = "'
        for i, detectorId in enumerate(detectorIds): 
            if i < len(detectorIds) -1:
                filter += detectorId["detectorId"] + '" || str(?classifier) = "'
            else:
                filter += detectorId["detectorId"] + '")'
        if len(detectorId) == 0:
            filter = ""
        queryBuilder = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX win: <http://wirtschaftsinformatik.uni-rostock.de/studentimagerecog#>
       
SELECT DISTINCT ?detected ?classifier ?subClassContexts

WHERE {
	?detected rdfs:subClassOf+ win:DetectedClasses ;
		win:ImageClassifier ?classifier .

	?context rdfs:subClassOf* win:context ;
            		rdfs:subClassOf [
            			owl:onProperty win:hasDetectedClass ;
           			owl:someValuesFrom ?detected ] .
	?subClassContexts rdfs:subClassOf* ?context
        """ + filter + "} "
        logging.debug(queryBuilder)
        print(queryBuilder)
        qres = self.rdf.query(queryBuilder)
        responseBuilder  = []
        
        for row in qres:
            responseBuilder.append({
                "objectName": re.sub("((.*)#)", "",str(row[0])),
                "imageClassifier": str(row[1]),
                "contextItems": re.sub("((.*)#)", "", str(row[2]))})
                
        return responseBuilder
