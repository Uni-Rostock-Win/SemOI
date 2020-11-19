from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
import os, re
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

        # Request Detection Type from the Radio Buttons/User Input
        modul = request.POST["modul"]

        # Save the File
        uploaded_file = request.FILES['inpFile']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)

        # Define the path for the loaded image and for the result image
        path_to_image = os.path.join(BASE_DIR, 'media/{0}'.format(uploaded_file.name))
        path_to_save = os.path.join(BASE_DIR, 'media/results/')
        path_to_annotatedImage = "media/results/" + uploaded_file.name
        fileType = re.findall("\.[a-zA-Z]*$", path_to_annotatedImage)[0]
        path_to_annotatedImage = re.sub("\.[a-zA-Z]*$", "_with_BOXES" + fileType, path_to_annotatedImage)
        
        # path_to_annotatedImage = re.sub("\\\\|\/", "/", path_to_annotatedImage)
        # path_to_annotatedImage = path_to_annotatedImage.replace("/", os.path.sep)
        print(path_to_annotatedImage)
        
        # Run Object Detection
        ObjList = run_object_detection(int(modul), path_to_image, path_to_save)

        # Convert the List to display in the Output Field
        ObjListHTML = convertList_toHTML(ObjList)
        # Get Scenes from the SemanticAPI
        SemaList = semanticCaller(ObjList)
        print(path_to_save)
        print(path_to_image)

        # Convert the List to display in the Ouput Field
        SemaListHTML =""
        
        SemaListHTML = convertList_toHTML(SemaList)
        print(path_to_annotatedImage)
        context= {
            'url' : fs.url(name),
            'ObjListHTML' : ObjListHTML,
            'SemaListHTML': SemaListHTML,
            'uploadedImage': path_to_annotatedImage,
            'result': True
         }

    return render(request, 'upload.html', context)


