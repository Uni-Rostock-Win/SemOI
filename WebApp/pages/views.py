from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
import os
from .semanticCaller import semanticCaller
import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Helper Function
def convertList_toHTML(mylist):
    a = '<br>'.join(mylist)
    return a

#Create your views here

def upload(request):
    context = {}
    if request.method == 'POST':

        # Request Detection Type from the Radio Buttons/User Input
        modul = request.POST["modul"]

        # Get the file and upload it to a temporary file
        uploaded_file = request.FILES['inpFile']
        #fs = FileSystemStorage()
        #name = fs.save(uploaded_file.name, uploaded_file)


        # Define the path for the loaded image and for the result image
        path_to_image = os.path.join(BASE_DIR, 'media/{0}'.format(uploaded_file.name))
        path_to_save = os.path.join(BASE_DIR, 'media/results/')

        # Run Object Detection
        ObjList = run_object_detection(int(modul), uploaded_file, path_to_save)
        #ObjList = ObjDet[0]
        #Image_with_Boxes = ObjDet[1]

        # Convert the List to display in the Output Field
        ObjListHTML = convertList_toHTML(ObjList)

        # Get Scenes from the SemanticAPI
        SemaList = semanticCaller(ObjList)
        # Convert the List to display in the Ouput Field
        for List in SemaList:
            SemaListHTML = convertList_toHTML(List)

        # Function to delete the saved files

        context= {
            'url' : fs.url(name),
            'ObjListHTML' : ObjListHTML,
            'SemaListHTML': SemaListHTML
           # 'Image_with_Boxes': Image_with_Boxes
         }

    return render(request, 'upload.html', context)


