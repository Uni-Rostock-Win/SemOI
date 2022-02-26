import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from numpy.lib.function_base import _calculate_shapes
from .tf_hub import run_object_detection
from .tf_hub import run_object_detection_Lite
from .semanticCaller import callSemantic
from .performance import PerformanceRegistry
import cv2
import time

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
    entries = ["Person: 27.4%",
               "Clothing: 15.2%",
               "Clothing: 14.1%",
               "Clothing: 13.5%",
               "Man: 10.8%",
               "Human arm: 10.6%",
               "Man: 10.4%",
               "Wine glass: 10.2%"]

    semantics = ["people: 100.0%",
                 "cooking: 12.7%",
                 "dining_room: 12.7%",
                 "kitchen: 12.7%",
                 "meal: 12.7%",
                 "party: 12.7%"]

    data = {
        "ObjListHTML": "<br>".join(entries),
        "SemaListHTML": "<br>".join(semantics),
        "resultImage": "../media/party-result.jpg"
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
        fs = FileSystemStorage(location="media/uploaded")
        name = fs.save(uploaded_file.name, uploaded_file)
        print("fs save name", name)

        # Define the path for the loaded image and for the result image
        source = os.path.join(BASE_DIR, "media", "uploaded" , uploaded_file.name)
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
def vidUpload(request):
    global source
    global destination

    registry = PerformanceRegistry()
    context = {}

    if request.method == "POST":
        # Save the File
        save_performance = registry.start("file-save")

        uploaded_file = request.FILES["inpFile2"]
        fs = FileSystemStorage(location="media/uploaded")
        name = fs.save(uploaded_file.name, uploaded_file)
        print("fs save name", name)

        # Define the path for the loaded image and for the result image
        source = os.path.join(BASE_DIR, "media", "uploaded" , uploaded_file.name)
        path_to_save = os.path.join(BASE_DIR, "media", "results")

        if not os.path.exists(path_to_save):
            print("creating path", path_to_save)
            os.mkdir(path_to_save)

        path_raw = os.path.join(path_to_save, uploaded_file.name)
        (file_name, file_extension) = os.path.splitext(path_raw)
        destination = file_name + "-result"

        print("source image", source)
        print("save image at", destination)
        save_performance.stop()

        uploaded_video_path = "/" + os.path.relpath(source, BASE_DIR).replace("\\", "/")  # windows quirk

        context = {
            "uploadedVideo": uploaded_video_path
        }

    return render(request, "vidUpload.html", context)


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
        # html_mapper = lambda x: "{0} @ score={1:3.1f}% rel-area={2:3.1f}%".format(x[0], x[1] * 100.0, x[3] * 100.0)
        html_mapper = lambda x: "{0}: {1:3.1f}%".format(x[0], x[1] * 100.0)
        object_list_html = html_list(map(html_mapper, detection_result))

        # Get Scenes from the SemanticAPI
        semantic_processing_performance = registry.start("semantic-detection")
        semantic = callSemantic()
        semanticResults = semantic.semanticCaller(detection_result)
        semantic_processing_performance.stop()
        
        # Convert the List to display in the Output Field
        semantic_list_html = html_list(semanticResults)
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

def count_els(e, labels):
  i = 0
  for el in labels:
    if el == e:
      i+=1
  return i

@csrf_exempt
def analyzeVideo(request):
    context = {}
    label_list = []
    registry = PerformanceRegistry()

    global source
    global destination
    global BASE_DIR

    base = os.path.splitext(os.path.basename(source))[0]

    #Start video capture and save width x height
    cap = cv2.VideoCapture(source)
    if (cap.isOpened() == False):
        print('Error while trying to read video. Please check path again')

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # define codec and create VideoWriter object 
    out = cv2.VideoWriter(destination+".mp4", cv2.VideoWriter_fourcc(*'h264'), 30, (frame_width, frame_height))

    # Define variables for process loop
    # frame_skip is the number of frames that are skipped before analyzing the current frame again (saves processing time)
    count = 0
    best_label = "no_activity"
    frame_skip = 0
    frame_skip_counter = 0

    if request.method == "POST":
        # Request Detection Type from the Radio Buttons/User Input
        module_identifier = request.POST["module-identifier"]
        print("module", module_identifier)

        #Request Frameskip Option from the Dropdown Input
        frameskip_chosen_option = request.POST["frameskip-option"]
        if frameskip_chosen_option == "none":
            pass
        else:
            frame_skip = int(frameskip_chosen_option)

        # Read until end of video
        while(cap.isOpened()):
            # Capture each frame of the video
            ret, frame = cap.read()
            if ret == True:
                #Analyzing process only looks at frames that are not skipped for increased efficieny and timesave
                if frame_skip_counter == 0:
                    frameImage = frame.copy()
                    best_label_count = 0

                    #Converting the frame from a numpy array into a readable .jpg file for detection
                    cv2.imwrite('./media/frames/'+ base + str(count) + '.jpg', frame)
                    image = "./media/frames/"+ base + str(count) +".jpg"

                    # Run Object Detection
                    detection_result = run_object_detection_Lite(module_identifier, image, registry)

                    # Get Scenes from the SemanticAPI
                    semantic_processing_performance = registry.start("semantic-detection")
                    semantic = callSemantic()
                    semanticResult = semantic.semanticCaller_V(detection_result)
                    semantic_processing_performance.stop()

                    #Build dynamic list for detected labels and corresponding frames
                    #and only keep the results of the last 10 Frames (removes label flickering)
                    label_list.append(semanticResult)
                    if(len(label_list) > 10):
                        del label_list[0]
                    else:
                        pass

                    #Extract label with most occurences (best label)
                    unique_labels = set(label_list)

                    for el in unique_labels:
                      if(count_els(el, label_list) > best_label_count):
                        best_label = el
                        best_label_count = count_els(el, label_list)
                      else:
                        pass

                    print("LABEL FOR THIS FRAME: "+best_label)
                    print("LABEL LISTE: "+str(label_list))
                    print("UNIQUE LABELS: "+str(unique_labels))

                    #Put Label on Frame (top left corner)
                    cv2.putText(frameImage, best_label, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, lineType=cv2.LINE_AA)

                    #Add frame with label to newly assembled video file
                    out.write(frameImage)

                    os.remove("./media/frames/"+ base + str(count) +".jpg")

                    if frame_skip == 0:
                        pass
                    else:
                        frame_skip_counter += 1
                else:
                    #skip analyzing step and put last known label on current frame
                    frameImage = frame.copy()

                    #Put Label on Frame (top left corner)
                    cv2.putText(frameImage, best_label, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, lineType=cv2.LINE_AA)

                    #Add frame with label to newly assembled video file
                    out.write(frameImage)

                    if frame_skip_counter < frame_skip:
                        frame_skip_counter += 1
                    else:
                        frame_skip_counter = 0
            else:
                break
            count += 1

        print("Video had "+str(count)+" analyzed frames.")

        # Release VideoCapture()
        cap.release()
        out.release()
        # Close all frames
        cv2.destroyAllWindows()

        #Wait a "few" seconds for the mp4 file to finish assembling for next steps
        time.sleep(30)

        result_video_path = "/" + os.path.relpath(destination+".mp4", BASE_DIR).replace("\\", "/")  # windows quirk
        print("result video path:", result_video_path)

        context = {
            "resultVideo": result_video_path,
            "result": True
        }

    render_performance = registry.start("rendering")
    render_result_2 = render(request, "vidResults.html", context)
    render_performance.stop()

    print("performance results")
    for e in registry.relative():
        e[2] *= 100.0
        print("{0:32s}{1:4.1f}s {2:5.1f}%".format(*e))

    return render_result_2
