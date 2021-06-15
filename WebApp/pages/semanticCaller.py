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
def semanticCaller(objects, ):
    scenes = []
    object_list_ids = []
    # Object List is in format "Footwear: 46%"
    # Convert it to only have "Footwear"

    id_index = build_object_index()

    post_data = {}

    for obj in objects:
        print("object", obj)
        parts = obj.split(":")
        object_name = parts[0]
        object_probability = parts[1]
        object_probability = object_probability.replace("%", "")
        object_probability = float(object_probability) / 100.0
        # Get the ID for the Semantic
        object_id = id_index[object_name]
        object_list_ids.append(str(object_id) + "=" + str(object_probability))
        post_data["data"] = str(object_list_ids)

    # Send the ID to the Semantic
    # depending whether the location is in a docker conainer, use localhost or the local docker instantiation
    is_docker_environemnt = os.environ.get("inDockerContainer", False)
    destination = "http://semanticapi:8000" if is_docker_environemnt else "http://localhost:8001"
    response = requests.post(destination, data=post_data)

    # Append only the Scenes from the Response to the SceneList
    try:
        for item in response.json():
            convert2Percent = round(float(response.json()[item]) * 100, 2)
            convert2Percent = str(convert2Percent) + "%"
            responseItem = str(item) + ": " + convert2Percent
            scenes.append(responseItem)
        # sceneList.append(response.json())
    # Catch IndexError for Objects which are not in the Semantic yet and append an empty list in this case
    except:
        pass

    return scenes
