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
        logging.debug(queryBuilder)
        qres = self.rdf.query(queryBuilder)
        responseBuilder  = []
        
        for row in qres:
            responseBuilder.append({
                "objectName": re.sub("((.*)#)", "",str(row[0])),
                "imageClassifier": str(row[1]),
                "scene": re.sub("((.*)#)", "", str(row[2]))})
                
        return self.scene2Array(responseBuilder)
