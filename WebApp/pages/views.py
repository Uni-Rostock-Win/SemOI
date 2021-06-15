import os
import time
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage
from .tf_hub import run_object_detection
from .semanticCaller import semanticCaller
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from performance import PerformanceRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def html_list(ls):
    return "<br>".join(ls)

#Create your views here
@csrf_exempt
def index(request):
    render_result = render(request, "index.html")
    return render_result

@csrf_exempt
def saveFile(request):
    context = {}
    registry = PerformanceRegistry()
    global destination
    global source
    if request.method == 'POST':        
        # Save the File
        save_performance = registry.start("file-save")
        
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
        print(os.path.relpath(destination, BASE_DIR))
        save_performance.stop()
        # context = {
        #     "uploadedImage": os.path.relpath(destination, BASE_DIR),
        # }
    render_result = render(request, "upload.html", context)
    return render_result

@csrf_exempt
def demo(request):
    ObjListHTML = [ "Person: 68%",
                    "Person: 51%",
                    "Drink: 44%",
                    "Man: 41%",
                    "Wine glass: 26%",
                    "Clothing: 25%",
                    "Human arm: 21%",
                    "Man: 21%",
                    "Drink: 18%"
                    ]
    SemaListHTML = ["dinner: 100.0%"]
    context = {
        "ObjListHTML" : "<br>".join(ObjListHTML),
        "SemaListHTML": "<br>".join(SemaListHTML),
        # "uploadedImage": os.path.relpath(destination, BASE_DIR),
        }
    render_result = render(request, "results.html", context)
    return render_result

@csrf_exempt
def upload(request):
    context = {}
    registry = PerformanceRegistry()

    if request.method == 'POST':
        # Request Detection Type from the Radio Buttons/User Input
        modul = request.POST["modul"]
        print("module", modul)
        print("dest", destination)
        print("src", source)
        # Run Object Detection
        object_detection_performance = registry.start("object-detection")
        ObjList = run_object_detection(int(modul), source, destination)
        object_detection_performance.stop()
        
        # Convert the List to display in the Output Field
        ObjListHTML = html_list(ObjList)

        # Get Scenes from the SemanticAPI
        semantic_processing_performance = registry.start("semantic-detection")
        SemaList = semanticCaller(ObjList)
        semantic_processing_performance.stop()

        # Convert the List to display in the Ouput Field
        SemaListHTML = html_list(SemaList)
        print("semantic list", SemaListHTML)

        context = {
            # "url" : fs.url(name),
            "ObjListHTML" : ObjListHTML,
            "SemaListHTML": SemaListHTML,
            "uploadedImage": os.path.relpath(destination, BASE_DIR),
            "result": True
         }

    render_performance = registry.start("rendering")
    render_result = render(request, "results.html", context)
    render_performance.stop()

    print("performance results")
    for e in registry.relative():
        e[2] *= 100.0
        print("{0:32s}{1:4.1f}s {2:5.1f}%".format(*e))

    return render_result


