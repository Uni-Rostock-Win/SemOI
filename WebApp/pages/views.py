from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Helper Function
def convertList_toHTML(mylist):
    a = '<br>'.join(mylist)
    return a

# Create your views here.
class Home(TemplateView):
    template_name = 'home1.html'

def home_view(request, *args, **kwargs):
   return render(request, "home.html", {})

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
        ObjList = run_object_detection(2, path_to_image, path_to_save)
        # Convert the List to display in the Output Field
        ObjList = convertList_toHTML(ObjList)

        context= {
            'url' : fs.url(name),
            'ObjList' : ObjList,
         }

    return render(request, 'upload.html', context)


