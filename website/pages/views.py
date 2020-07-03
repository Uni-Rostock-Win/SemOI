from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage

# Create your views here.
class Home(TemplateView):
    template_name = 'home1.html'

def home_view(request, *args, **kwargs):
   return render(request, "home.html", {})

def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file, max_length=1024*1024*16)
        context['url']= fs.url(name)
    return render(request, 'upload.html', context)