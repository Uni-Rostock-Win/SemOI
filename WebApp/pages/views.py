from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
import os
from .semanticCaller import semanticCaller

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Helper Function
def convertList_toHTML(mylist):
    a = '<br>'.join(mylist)
    return a

#Create your views here
def upload(request):
    context = {}
    if request.method == 'POST':
        # Save the File
        uploaded_file = request.FILES['inpFile']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file, max_length=1024*1024*16)
        # Define the path for the loaded image and for the result image
        path_to_image = os.path.join(BASE_DIR, 'media/{0}'.format(uploaded_file.name))
        path_to_save = os.path.join(BASE_DIR, 'media/results/')
        # Run Object Detection
        # 1 for accurate Detection, 2 for fast Detection
        ## (How to import the radio button here so you can choose between fast and accurate?)
        ObjList = run_object_detection(2, path_to_image, path_to_save)
        # Convert the List to display in the Output Field
        ObjListHTML = convertList_toHTML(ObjList)

        # Get Scenes from the SemanticAPI
        SemaList = semanticCaller(ObjList)
        for List in SemaList:
            SemaList = convertList_toHTML(List)


        context= {
            'url' : fs.url(name),
            'ObjListHTML' : ObjListHTML,
            'SemaList': SemaList
         }

    return render(request, 'upload.html', context)


