import os
import requests


# Returns the ObjID from a LabelMap
# We need this because the SemanticAPI only accepts the ObjectID from an OpenImage Object
# We should use oidv4_LabelMap. Which is the Map for OpenImage
# Get them here while they are hot: https://github.com/tensorflow/models/tree/master/research/object_detection/data
# Must have the following format:
# item {
#   name: ""
#   id: 
#   display_name: ""
# }

class ObjectDefinitionAccess:

    def __init__(self):
        pass

    def definitions(self, source):
        block_name = ""
        block_content = ""

        state = False

        for line in source:
            for c in line:
                if c == "{":
                    state = True
                elif c == "}":
                    yield self.parse_block(block_name, block_content)
                    state = False
                    block_name = ""
                    block_content = ""
                else:
                    if state:
                        block_content += c
                    else:
                        block_name += c

    def parse_block(self, name, content):
        items = {}

        lines = filter(lambda x: x, map(lambda x: x.strip(), content.splitlines()))

        for line in lines:
            i = line.index(":")
            j = i + 1
            key = line[0:i].strip()
            value = line[j:].strip()
            items[key] = self.replace_escapes(value)

        return name.strip(), items

    @staticmethod
    def replace_escapes(part):
        result = ""

        ignore = False

        for c in part:
            if ignore:
                result += c
                ignore = False
                continue

            if c == "\\":
                ignore = True
                continue

            if c != "\"":
                result += c

        return result


def build_object_index():
    index = {}

    with open("oidv4_LabelMap.txt", "r") as source:
        access = ObjectDefinitionAccess()
        for (name, items) in access.definitions(source):
            key = items["display_name"]
            value = items["name"]
            index[key] = value

    return index


# Function to get the Scenes from the API
def semanticCaller(detection_result):
    scenes = []
    object_list_ids = []
    id_index = build_object_index()
    post_data = {}

    for entry in detection_result:
        object_name = entry[0]
        object_probability = entry[1]
        object_size = entry[2][2]*entry[2][3]
        object_relevance = object_probability * object_size

        # Get the ID for the Semantic
        object_id = id_index[object_name]
        object_list_ids.append(str(object_id) + "=" + str(object_relevance))
        post_data["data"] = str(object_list_ids)

    # Send the ID to the Semantic
    # depending whether the location is in a docker conainer, use localhost or the local docker instantiation
    is_docker_environment = os.environ.get("inDockerContainer", False)
    destination = "http://semanticapi:8000" if is_docker_environment else "http://localhost:8001"
    response = requests.post(destination, data=post_data)

    # Append only the Scenes from the Response to the SceneList

    parsed = response.json()

    for key in parsed:
        scenes.append("{0}: {1:.1f}%".format(str(key), float(parsed[key] * 100.0)))

    return scenes
