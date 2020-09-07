import linecache
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
def return_ObjID_from_ObjectName(Object):
    labelMap = "oidv4_LabelMap.txt"
    line_number = 0
    with open(labelMap, 'r') as read_obj:
        for line in read_obj:
            # For each line, check if the Line contains the string
            line_number += 1
            if Object in line:
                # If yes, then go up 2 lines and assign the line to ObjID
                line_number -= 2
                ObjID = linecache.getline(labelMap, line_number)
                # ObjID should be now: name: "/m/01nkt"
                # We only want the ObjectID number between the " " 
                # So lets slice the line and only take the String between the quotation marks
                ObjID = ObjID.split("\"")[1]
                return ObjID




# Function to get the Scenes from the API
def semanticCaller(ObjectList):

    sceneList = []
    # Object List is in format "Footwear: 46%"
    # Convert it to only have "Footwear"
    for Object in ObjectList:
        Object = Object.split(":")[0]
        # Get the ID for the Semantic 
        ObjectID = return_ObjID_from_ObjectName(Object)
        # Send the ID to the Semantic
        response = requests.get('http://semanticapi:8000?objectID1={0}'.format(ObjectID))
        # Append only the Scenes from the Response to the SceneList
        try:
            sceneList.append(response.json()[2]["scenes"])
        # Catch IndexError for Objects which are not in the Semantic yet and append an empty list in this case
        except : 
            pass
    return(sceneList)






