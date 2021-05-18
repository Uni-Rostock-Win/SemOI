import os
import json
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
            
        return (name.strip(), items)

    def replace_escapes(self, part):
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
    ObjectListIDs = []
    # Object List is in format "Footwear: 46%"
    # Convert it to only have "Footwear"

    id_index = build_object_index()

    for obj in objects:
        print("object", obj)
        parts = obj.split(":")
        ObjectName = parts[0]
        ObjectProbability = parts[1]
        ObjectProbability = ObjectProbability.replace("%", "")
        ObjectProbability = float(ObjectProbability) / 100.0
        # Get the ID for the Semantic 
        ObjectID = id_index[ObjectName]
        ObjectListIDs.append(str(ObjectID) + "=" + str(ObjectProbability))
        postObject = {"data": str(ObjectListIDs)}

    # Send the ID to the Semantic
    #depending whether the location is in a docker conainer, use localhost or the local docker instantiation
    dockerCheck = os.environ.get("inDockerContainer", False)
    targetUrl = "http://semanticapi:8000" if dockerCheck else "http://localhost:8001"
    response = requests.post(targetUrl, data=postObject) 

    # Append only the Scenes from the Response to the SceneList
    try:
        for item in response.json():
            convert2Percent = round(float(response.json()[item])* 100, 2)
            convert2Percent = str(convert2Percent) + "%"
            responseItem = str(item) +": " + convert2Percent
            scenes.append(responseItem)
        # sceneList.append(response.json())
    # Catch IndexError for Objects which are not in the Semantic yet and append an empty list in this case
    except : 
        pass

    return(scenes)
