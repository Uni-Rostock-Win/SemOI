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
    if request.method == 'GET':
        sh = SemanticHandler()
        oID1 = request.GET.get('objectID1')
        if(oID1 == None or not(oID1.startswith("/m/"))):
            raise WrongInputData
        semanticResponse = sh.getSemanticEnhancement(oID1)
        return Response(semanticResponse)
    
    if request.method == 'POST':
        
        sh = SemanticHandler()
        data = request.data
        ProbAggregation = {}
        print("req:")
        print(data)
        print("data: ")
        print(data["data"])
        newData = re.sub("\s|\[|\]|\'", "",  str(data["data"]))
        print("regex_cleared")
        print(newData)
        array = str(newData).split(",")
        
        print(array)
        
        
        maxValue = 0.0
        detectedObjects = []
        
        for detectedObject in array:
            detectedObjects.append({
                "detectorId":  detectedObject.split("=")[0],
                "probability":  float(detectedObject.split("=")[1])
                })

        semanticResponse = sh.getSemanticEnhancement(detectedObjects)
        inferedElements = {}
        for detectedObject in detectedObjects:
            inferedElementsForOneDetector = filterSemanticResponse(detectedObject["detectorId"], semanticResponse)
            for inferedElement in inferedElementsForOneDetector:
                if(inferedElement in inferedElements):
                    inferedElements[inferedElement] += detectedObject["probability"]
                else:
                    inferedElements[inferedElement] =  detectedObject["probability"]
                maxValue = inferedElements[inferedElement] if maxValue < inferedElements[inferedElement] else maxValue
        
        # Normalize Values
        for element in inferedElements:
            inferedElements[element] /= maxValue

        return Response(inferedElements)

def filterSemanticResponse(detectorId: str, semanticRespose: list):
    contextList = []
    for element in semanticRespose:
        if(detectorId == element["imageClassifier"]):
            contextList.append(element["contextItems"])
    return contextList
