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
        for element in array:
            print(element)
            id = element.split("=")[0]
            prob = element.split("=")[1]
            semanticResponse = sh.getSemanticEnhancement(id)
            print(semanticResponse)
            for responseElement in semanticResponse[0]["scenes"]:
                if responseElement in ProbAggregation:
                    ProbAggregation[responseElement] = ProbAggregation[responseElement] + float(prob)
                else:
                    ProbAggregation[responseElement] = float(prob)
                    print(prob)
                    print("created")
                if (ProbAggregation[responseElement] > maxValue):
                    maxValue = ProbAggregation[responseElement] 
        # Normalize Values
        for item in ProbAggregation:
            ProbAggregation[item] = ProbAggregation[item] / maxValue

        return Response(ProbAggregation)