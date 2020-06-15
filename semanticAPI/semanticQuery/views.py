from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from SemanticHandler import SemanticHandler
from semanticQuery.Exceptions import WrongInputData

#import SemanticHandler.py
# Create your views here.


@api_view(['GET'])
def semanticCall(request):
    sh = SemanticHandler()
    oID1 = request.GET.get('objectID1')
    if(oID1 == None or not(oID1.startswith("/m/"))):
        raise WrongInputData
    semanticResponse = sh.getSemanticEnhancement(oID1)
    return Response(semanticResponse)