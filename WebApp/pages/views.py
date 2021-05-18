import os
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
from .semanticCaller import semanticCaller
from django.views.decorators.csrf import csrf_exempt, csrf_protect

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def html_list(ls):
    return "<br>".join(ls)

#Create your views here
@csrf_exempt
def upload(request):
    context = {}

    if request.method == 'POST':
        # Request Detection Type from the Radio Buttons/User Input
        modul = request.POST["modul"]
        print("module", modul)
        
        # Save the File
        uploaded_file = request.FILES["inpFile"]
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        print("fs save name", name)
        
        # Define the path for the loaded image and for the result image
        source = os.path.join(BASE_DIR, "media", uploaded_file.name)
        path_to_save = os.path.join(BASE_DIR, "media", "results")

        if not os.path.exists(path_to_save):
            print("creating path", path_to_save)
            os.mkdir(path_to_save)

        path_raw = os.path.join(path_to_save, uploaded_file.name)
        (file_name, file_extension) = os.path.splitext(path_raw);
        destination = file_name + "-result" + file_extension

        print("source image", source)
        print("save image at", destination)
        
        # Run Object Detection
        ObjList = run_object_detection(int(modul), source, destination)

        # Convert the List to display in the Output Field
        ObjListHTML = html_list(ObjList)
        # Get Scenes from the SemanticAPI
        SemaList = semanticCaller(ObjList)

        # Convert the List to display in the Ouput Field
        SemaListHTML = html_list(SemaList)
        print("semantic list", SemaListHTML)

        context = {
            "url" : fs.url(name),
            "ObjListHTML" : ObjListHTML,
            "SemaListHTML": SemaListHTML,
            "uploadedImage": os.path.relpath(destination, BASE_DIR),
            "result": True
         }

    return render(request, "upload.html", context)


