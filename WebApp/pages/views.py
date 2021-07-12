import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .tf_hub import run_object_detection
from .semanticCaller import semanticCaller
from .performance import PerformanceRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

source = ""
destination = ""


def html_list(ls):
    return "<br>".join(ls)


@csrf_exempt
def index(request):
    return render(request, "index.html")


@csrf_exempt
def demo(request):
    entries = ["Person: 68%",
               "Person: 51%",
               "Drink: 44%",
               "Man: 41%",
               "Wine glass: 26%",
               "Clothing: 25%",
               "Human arm: 21%",
               "Man: 21%",
               "Drink: 18%"]

    semantics = ["dinner: 100.0%"]

    data = {
        "ObjListHTML": "<br>".join(entries),
        "SemaListHTML": "<br>".join(semantics),
    }

    return render(request, "results.html", data)


@csrf_exempt
def upload(request):
    global source
    global destination

    registry = PerformanceRegistry()
    context = {}

    if request.method == "POST":
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
        (file_name, file_extension) = os.path.splitext(path_raw)
        destination = file_name + "-result" + file_extension

        print("source image", source)
        print("save image at", destination)
        save_performance.stop()

        uploaded_image_path = "/" + os.path.relpath(source, BASE_DIR).replace("\\", "/")  # windows quirk

        context = {
            "uploadedImage": uploaded_image_path
        }

    return render(request, "upload.html", context)


@csrf_exempt
def analyze(request):
    context = {}
    registry = PerformanceRegistry()

    global source
    global destination
    global BASE_DIR

    if request.method == "POST":
        # Request Detection Type from the Radio Buttons/User Input
        module_identifier = request.POST["module-identifier"]
        print("module", module_identifier)

        # Run Object Detection
        detection_result = run_object_detection(module_identifier, source, destination, registry)

        # Convert the List to display in the Output Field
        html_mapper = lambda x: "{0} @ score={1:3.1f}% rel-area={2:3.1f}%".format(x[0], x[1] * 100.0, x[3] * 100.0)
        object_list_html = html_list(map(html_mapper, detection_result))

        # Get Scenes from the SemanticAPI
        semantic_processing_performance = registry.start("semantic-detection")
        semantics = semanticCaller(detection_result)
        semantic_processing_performance.stop()

        # Convert the List to display in the Output Field
        semantic_list_html = html_list(semantics)
        print("semantic list", semantic_list_html)

        result_image_path = "/" + os.path.relpath(destination, BASE_DIR).replace("\\", "/")  # windows quirk
        print("result image path:", result_image_path)

        context = {
            "ObjListHTML": object_list_html,
            "SemaListHTML": semantic_list_html,
            "resultImage": result_image_path,
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
