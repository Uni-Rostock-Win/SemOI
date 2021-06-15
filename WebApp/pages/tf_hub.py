import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps


# Print Tensorflow version
print(tf.__version__)
# Check available GPU devices.
print("The following GPU devices are available: %s" % tf.test.gpu_device_name())


def limit_image_size(image_data):
    width, height = image_data.size
    pixels = width * height

    # 8 Megapixels
    target = 8_000_000

    if pixels > target:
        factor = target / pixels
        print("resizing image by factor", factor)
        return ImageOps.scale(image_data, factor, Image.BICUBIC)
    else:
        return image_data


# preprocess the image by loading it from a source path and resize it if necessary
def preprocess_image(source_path):
    image_raw = Image.open(source_path)
    image_rgb = image_raw.convert("RGB")
    resized = limit_image_size(image_rgb)

    return image_rgb, resized, tf.keras.preprocessing.image.img_to_array(resized)


def draw_bounding_box_on_image(image,
                               ymin,
                               xmin,
                               ymax,
                               xmax,
                               color,
                               font,
                               thickness=4,
                               display_str_list=()):
    """Adds a bounding box to an image."""

    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size

    left = xmin * im_width
    right = xmax * im_width
    top = ymin * im_height
    bottom = ymax * im_height

    draw.line([(left, top), (left, bottom), (right, bottom), (right, top),
               (left, top)],
              width=thickness,
              fill=color)

    # If the total height of the display strings added to the top of the bounding
    # box exceeds the top of the image, stack the strings below the bounding box
    # instead of above.
    display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]
    # Each display_str has a top and bottom margin of 0.05x.
    total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = top + total_display_str_height
    # Reverse list and print from bottom to top.
    for display_str in display_str_list[::-1]:
        text_width, text_height = font.getsize(display_str)
        margin = np.ceil(0.05 * text_height)
        draw.rectangle([(left, text_bottom - text_height - 2 * margin),
                        (left + text_width, text_bottom)],
                       fill=color)
        draw.text((left + margin, text_bottom - text_height - margin),
                  display_str,
                  fill="black",
                  font=font)
        text_bottom -= text_height - 2 * margin


def draw_boxes(image_pil, boxes, class_names, scores, max_boxes=10, min_score=0.1):
    """Overlay labeled boxes on an image with formatted scores and label names."""
    colors = list(ImageColor.colormap.values())

    font = ImageFont.load_default()

    object_list = []

    for i in range(min(boxes.shape[0], max_boxes)):
        if scores[i] >= min_score:
            ymin, xmin, ymax, xmax = tuple(boxes[i])

            class_name = class_names[i].decode("ascii")
            score = int(100 * scores[i])
            display_str = "{}: {}%".format(class_name, score)

            color = colors[hash(class_names[i]) % len(colors)]

            draw_bounding_box_on_image(
                image_pil,
                ymin,
                xmin,
                ymax,
                xmax,
                color,
                font,
                display_str_list=[display_str])

            object_list.append(display_str)

    return object_list


# Function to run the actual Object Detection
# Choose Module
# high accuracy = 1 (FasterRCNN + InceptionResNet V2)
# small and fast = 2 (SSD + MobileNet V2)
# EXAMPLE USE: run_object_detection(2, 'images/image1.jpg', 'images/results/', performance_registry)
def run_object_detection(module, source, destination, registry):
    if module == 1:
        module_handle = 'https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1'
    elif module == 2:
        module_handle = 'https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1'
    else:
        print("Invalid Module number")
        return 0

    detector_load_performance = registry.start("detector-load")
    detector = hub.load(module_handle).signatures['default']
    detector_load_performance.stop()

    image_load_performance = registry.start("image-load")
    image_rgb, image_resized, tf_image_data = preprocess_image(source)
    image_load_performance.stop()

    image_convert_performance = registry.start("image-convert")
    converted_img = tf.image.convert_image_dtype(tf_image_data, tf.float32)[tf.newaxis, ...]
    image_convert_performance.stop()

    image_detect_performance = registry.start("detect")
    object_detection_result = detector(converted_img)
    image_detect_performance.stop()

    image_boxing_performance = registry.start("boxing")
    result = {key: value.numpy() for key, value in object_detection_result.items()}

    boxes = result["detection_boxes"]
    entities = result["detection_class_entities"]
    scores = result["detection_scores"]

    object_list = draw_boxes(image_resized, boxes, entities, scores)
    image_boxing_performance.stop()

    # Save the image
    image_save_performance = registry.start("image-save")
    image_resized.save(destination, '')
    image_save_performance.stop()

    return object_list
