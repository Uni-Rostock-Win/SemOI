import os
import requests

from pages.SemanticHandler import SemanticHandler

class callSemantic:
    # Function to get the Scenes from the API
    def semanticCaller(self, detection_results):

        maxValue = 0
        sh = SemanticHandler()
        # Call the Semantic
        semanticResponse = sh.getSemanticEnhancement(detection_results)
        inferedElements = {}
        # Calculte the semantic Confidence Value.
        for detectedObject in detection_results:
            # Access at first just one detected element
            inferedElementsForOneDetector = self.filterSemanticResponse(detectedObject[4], semanticResponse)
            # For this detected element, iterate over the inferred items by the semantic
            for inferedElement in inferedElementsForOneDetector:
                # If the infered item already has been detected
                if(inferedElement in inferedElements):
                    # Then set the counter of the amount of detected elements +1
                    inferedElements[inferedElement] += detectedObject[1]
                    print(self.getRelationCountForInferredElement(semanticResponse, inferedElement)) # Just as a placeholder and an Example!
                else:
                    # Otherwise add the element to the dict
                    inferedElements[inferedElement] =  detectedObject[1]
                # Calculates the highest counter over all elements.
                maxValue = inferedElements[inferedElement] if maxValue < inferedElements[inferedElement] else maxValue
        
        scenes = []
        # Normalize Values
        for element in inferedElements:
            inferedElements[element] /= (maxValue /100)
            scenes.append("{0}: {1:.1f}%".format(str(element), float(inferedElements[element])))
        
        

        return scenes


    def getRelationCountForInferredElement(self, semanticResponse: list,  inferredElement: str)->int:
        """Get the amount of Realations of one inferred item

        Args:
            semanticResponse (list): The respone from the getSemanticEnhancement method
            inferredElement (str): The item to look at

        Raises:
            LookupError: The item is not in the return list of the semantic response

        Returns:
            int: Count of relations of the inferredElement items
        """
        for item in semanticResponse:
            if(inferredElement == item["contextItems"]):
                return item["numberOfRelations"]
        # No element is found
        raise LookupError( "Contextitem not in resultlist")

    def filterSemanticResponse(self, detectorId: str, semanticRespose: list)->list:
        """Takes the response of the semantic and isolates the results for ONE detector

        Args:
            detectorId (str): detector to be filtered
            semanticRespose (list): Array List Containing the semantic response

        Returns:
            list: list with inferred items for ONE detector
        """
        contextList = []
        for element in semanticRespose:
            if(detectorId == element["imageClassifier"]):
                contextList.append(element["contextItems"])
        return contextList

