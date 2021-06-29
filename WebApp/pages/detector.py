import tensorflow_hub as hub


class DetectorManager:

    def __init__(self):
        self._descriptors = {
            # "resnet-v2": {
            #     "name": "Inception Resnet v2",
            #     "description": "slower, but more accurate",
            #     "handle": "https://tfhub.dev/google/faster_rcnn/openimages_v4/inception_resnet_v2/1"
            # },
            "mobilenet-v2": {
                "name": "MobileNet version 2",
                "description": "faster, but less accurate",
                "handle": "https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1"
            }
        }

        self.storage = {}

    def load_all_detectors(self):
        iterations = 0
        for identifier, descriptor in self._descriptors.items():
            handle = descriptor["handle"]
            print("[detectors] loading detector", handle)
            self.storage[identifier] = hub.load(handle).signatures["default"]
            iterations += 1
        print("loaded", iterations, "detectors")

    def get_detector(self, identifier):
        if identifier in self.storage:
            return self.storage[identifier]
        else:
            raise AssertionError("no such tf detector:", identifier)

    def get_descriptors(self):
        return self._descriptors

