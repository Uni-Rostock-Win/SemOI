from logging import error
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SemanticHandler import SemanticHandler
import re
from semanticQuery.Exceptions import WrongInputData

#import SemanticHandler.py
# Create your views here.


@api_view(['GET', 'POST'])

def semanticCall(request):
    # This part here for "GET" is no longer used
    if request.method == 'GET':
        raise WrongInputData
        return Response(semanticResponse)
    
    if request.method == 'POST':
        
        sh = SemanticHandler()
        data = request.data
        ProbAggregation = {}

        newData = re.sub("\s|\[|\]|\'", "",  str(data["data"]))
        array = str(newData).split(",")
    
        maxValue = 0.0
        detectedObjects = []
        
        for detectedObject in array:
            detectedObjects.append({
                "detectorId":  detectedObject.split("=")[0],
                "probability":  float(detectedObject.split("=")[1])
                })
        # Call the Semantic
        semanticResponse = sh.getSemanticEnhancement(detectedObjects)
        inferedElements = {}
        # Calculte the semantic Confidence Value.
        for detectedObject in detectedObjects:
            # Access at first just one detected element
            inferedElementsForOneDetector = filterSemanticResponse(detectedObject["detectorId"], semanticResponse)
            # For this detected element, iterate over the inferred items by the semantic
            for inferedElement in inferedElementsForOneDetector:
                # If the infered item already has been detected
                if(inferedElement in inferedElements):
                    # Then set the counter of the amount of detected elements +1
                    inferedElements[inferedElement] += detectedObject["probability"]
                    print(getRelationCountForInferredElement(semanticResponse, inferedElement)) # Just as a placeholder and an Example!
                else:
                    # Otherwise add the element to the dict
                    inferedElements[inferedElement] =  detectedObject["probability"]
                # Calculates the highest counter over all elements.
                maxValue = inferedElements[inferedElement] if maxValue < inferedElements[inferedElement] else maxValue
        
        # Normalize Values
        for element in inferedElements:
            inferedElements[element] /= maxValue

        return Response(inferedElements)
    
def getRelationCountForInferredElement(semanticResponse: list,  inferredElement: str)->int:
    """Get the amount of Realtions of one inferred item

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

def filterSemanticResponse(detectorId: str, semanticRespose: list)->list:
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
