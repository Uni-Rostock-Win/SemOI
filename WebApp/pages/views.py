import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from .tf_hub import run_object_detection
from .semanticCaller import semanticCaller
from .performance import PerformanceRegistry

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def html_list(ls):
    return "<br>".join(ls)


@csrf_exempt
def upload(request):
    context = {}
    registry = PerformanceRegistry()

    if request.method == "POST":
        # Request Detection Type from the Radio Buttons/User Input
        module_identifier = request.POST["module-identifier"]
        print("module", module_identifier)

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

        # Run Object Detection
        detection_result = run_object_detection(module_identifier, source, destination, registry)

        # Convert the List to display in the Output Field
        html_mapper = lambda x: "{0} @ score={1:3.1f}% rel-area={2:3.1f}%".format(x[0], x[1] * 100.0, x[3] * 100.0)
        ObjListHTML = html_list(map(html_mapper, detection_result))

        # Get Scenes from the SemanticAPI
        semantic_processing_performance = registry.start("semantic-detection")
        SemaList = semanticCaller(detection_result)
        semantic_processing_performance.stop()

        # Convert the List to display in the Output Field
        SemaListHTML = html_list(SemaList)
        print("semantic list", SemaListHTML)

        uploaded_image_path = os.path.relpath(destination, BASE_DIR).replace("\\", "/")  # windows quirk
        print("uploaded image path:", uploaded_image_path)

        context = {
            "url": fs.url(name),
            "ObjListHTML": ObjListHTML,
            "SemaListHTML": SemaListHTML,
            "uploadedImage": uploaded_image_path,
            "result": True
        }

    render_performance = registry.start("rendering")
    render_result = render(request, "upload.html", context)
    render_performance.stop()

    print("performance results")
    for e in registry.relative():
        e[2] *= 100.0
        print("{0:32s}{1:4.1f}s {2:5.1f}%".format(*e))

    return render_result
