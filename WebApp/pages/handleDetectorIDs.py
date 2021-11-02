import json
class HandleDetectorIDs:
    """Read the list of Object Identifiers and transfers it into a KV-List

    Returns:
        dict: "detectorName": "Id"

    """
    kv = {}
    def __init__(self, *args, **kwargs):
        
        with open("oidv4_LabelMap.txt", "r") as source:
            for (name, item) in self.definitions(source):
                self.kv.update({item["display_name"] : item["name"]})
        
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
