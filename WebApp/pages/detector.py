import tensorflow_hub as hub


class DetectorManager:

    def __init__(self):
        self._handles = [
            #  "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1",
            "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
        ]

        self.storage = {}


    def load_all_detectors(self):
        iterations = 0
        for handle in self._handles:
            print("[detectors] loading detector", handle)
            self.storage[handle] = hub.load(handle).signatures["default"]
            iterations += 1

        print("loaded", iterations, "detectors")

    def get_detector(self, handle):
        if handle in self.storage:
            return self.storage[handle]
        else:
            raise AssertionError("no such tf detector:", handle)

