from collections import namedtuple
import tempfile
import os
import tensorflow as tf
import numpy as np
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from .detector import DetectorManager

# Print Tensorflow version
print(tf.__version__)
# Check available GPU devices.
print("The following GPU devices are available: %s" % tf.test.gpu_device_name())

_detector_manager = DetectorManager()
print("loading detectors")
_detector_manager.load_all_detectors()
print("detectors loaded")

image_dimension_tuple = namedtuple("ImageDimensions", ["width", "height", "size"])
image_box_tuple = namedtuple("ImageDetectionBox", ["x1", "y1", "x2", "y2"])


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

    width, height = resized.size
    size = width * height
    dimension = image_dimension_tuple(width, height, size)

    fd, temp_file_path = tempfile.mkstemp(suffix=".jpeg")
    try:
        resized.save(temp_file_path, format="JPEG", quality=90)
        print("temporary file path", temp_file_path)

        # tf_image = tf.keras.preprocessing.image.img_to_array(resized)
        tf_image_content = tf.io.read_file(temp_file_path)
        tf_image = tf.image.decode_jpeg(tf_image_content, channels=3)
    finally:
        os.close(fd)
        os.remove(temp_file_path)

    return dimension, image_rgb, resized, tf_image


def draw_bounding_box_on_image(image,
                               position,
                               color,
                               font,
                               thickness=4,
                               display_str_list=()):
    """Adds a bounding box to an image."""

    draw = ImageDraw.Draw(image)

    left = position.x1
    right = position.x2
    top = position.y1
    bottom = position.y2

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


def draw_boxes(image_pil, spliced):
    """Overlay labeled boxes on an image with formatted scores and label names."""
    colors = list(ImageColor.colormap.values())
    font = ImageFont.load_default()

    for entry in spliced:
        class_name = entry[0]
        score = int(100 * entry[1])
        display_str = "{}: {}%".format(class_name, score)

        color = colors[hash(class_name) % len(colors)]

        draw_bounding_box_on_image(
            image_pil,
            entry[2],
            color,
            font,
            display_str_list=[display_str])


def splice_result(object_detection_result, image_dimensions, item_limit=10, min_score=0.1):
    result = {key: value.numpy() for key, value in object_detection_result.items()}
    # print("all detected Objects", object_detection_result)
    positions = result["detection_boxes"]
    entities = result["detection_class_entities"]
    scores = result["detection_scores"]

    image_width = float(image_dimensions.width)
    image_height = float(image_dimensions.height)
    float_size = float(image_dimensions.size)

    ls = []
    entries = len(entities)
    processed = 0
    for i in range(0, entries):
        if processed >= item_limit:
            break

        entity = entities[i].decode("utf-8")
        score = scores[i]
        rel_position = positions[i]

        position = image_box_tuple(rel_position[1] * image_width, rel_position[0] * image_height,
                                   rel_position[3] * image_width, rel_position[2] * image_height)

        if score < min_score:
            break

        covered_area = (position.x2 - position.x1) * (position.y2 - position.y1)
        importance = covered_area / float_size
        print("entity", entity, "covered area", covered_area, "importance", importance)
        if importance < 0.1 and score < 0.3:
            continue

        ls.append((entity, score, position, importance))

        processed += 1

    return ls


# Function to run the actual Object Detection
# Choose Module
# high accuracy = 1 (FasterRCNN + InceptionResNet V2)
# small and fast = 2 (SSD + MobileNet V2)
def run_object_detection(module_identifier, source, destination, registry):
    detector_load_performance = registry.start("detector-load")
    detector = _detector_manager.get_detector(module_identifier)
    detector_load_performance.stop()

    image_load_performance = registry.start("image-load")
    image_dimension, image_rgb, image_resized, tf_image_data = preprocess_image(source)
    image_load_performance.stop()

    image_convert_performance = registry.start("image-convert")
    converted_img = tf.image.convert_image_dtype(tf_image_data, tf.float32)[tf.newaxis, ...]
    image_convert_performance.stop()

    image_detect_performance = registry.start("detect")
    object_detection_result = detector(converted_img)
    image_detect_performance.stop()

    spliced = splice_result(object_detection_result, image_dimension, 20, 0.1)

    image_boxing_performance = registry.start("boxing")
    draw_boxes(image_resized, spliced)
    image_boxing_performance.stop()

    image_save_performance = registry.start("image-save")
    image_resized.save(destination, '')
    image_save_performance.stop()

    return spliced
