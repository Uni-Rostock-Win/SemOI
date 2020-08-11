from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create your views here.
class Home(TemplateView):
    template_name = 'home1.html'

def home_view(request, *args, **kwargs):
   return render(request, "home.html", {})

def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['inpFile']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file, max_length=1024*1024*16)
        path_to_image = os.path.join(BASE_DIR, 'media/{0}'.format(uploaded_file.name))
        path_to_save = os.path.join(BASE_DIR, 'media/results/')
        ObjList = run_object_detection(2, path_to_image, path_to_save)
        context= {
            'url' : fs.url(name),
            'ObjList' : ObjList,
         }

    return render(request, 'upload.html', context)


