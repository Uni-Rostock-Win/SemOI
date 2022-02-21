import re, os, rdflib, logging


class SemanticHandler_I():
    
    
    def __init__(self):
        
        self.rdf = rdflib.Graph(store="OxMemory")
        self.rdf.parse(location="media/augmentionOntology_Images.owl", format="application/rdf+xml")
    
    def getSemanticEnhancement(self, detectorIds: list):
        filter =   'FILTER(str(?classifier) = "'
        for i, detectorId in enumerate(detectorIds): 
            if i < len(detectorIds) -1:
                filter += detectorId[4] + '" || str(?classifier) = "'
            else:
                filter += detectorId[4] + '")'
        if len(detectorId) == 0:
            filter = ""
        queryBuilder = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX win: <http://wirtschaftsinformatik.uni-rostock.de/studentimagerecog#>
       
SELECT  ?detected ?classifier ?context (Count(DISTINCT ?allContextConnections) as ?relationCount)

WHERE {
        ?detected rdfs:subClassOf+ win:DetectedClasses ;
                win:ImageClassifier ?classifier .

        ?context rdfs:subClassOf* win:context ;
                       rdfs:subClassOf [
                                owl:onProperty win:hasDetectedClass ;
                                owl:someValuesFrom ?detected ] .
        ?context rdfs:subClassOf [
                 	owl:onProperty win:hasDetectedClass ;
                    owl:someValuesFrom ?allContextConnections ] .
        """ + filter + """
}
GROUP BY ?detected ?classifier ?context 
ORDER BY ?detected ?context"""
        logging.debug(queryBuilder)
        print(queryBuilder)
        qres = self.rdf.query(queryBuilder)
        responseBuilder  = []
        # Converts the SPARQL-Query to a Dict-Array
        for row in qres:
            responseBuilder.append({
                "objectName": re.sub("((.*)#)", "",str(row[0])),
                "imageClassifier": str(row[1]),
                "contextItems": re.sub("((.*)#)", "", str(row[2])),
                "numberOfRelations" :  int(row[3])
                })
                
        return responseBuilder
