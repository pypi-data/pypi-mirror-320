
import os
import json
import logging

class JSONPreprocess(object):
    def __init__(self, json_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_file = json_file

    def load_json(self):
        with open(self.json_file) as json_file:
            self.baseline_json = json.load(json_file)

    def reorder(self):
        self.load_json()
        temp_dic = self.baseline_json.copy()
        new_node_list = []
        for n, node in enumerate(list(self.baseline_json["nodes"])):
            if node["type"]=="reservoir":
                pass
            else:
                new_node_list.append(node)

        for n, node in enumerate(list(self.baseline_json["nodes"])):
            if node["type"]=="reservoir":
                new_node_list.append(node)
            else:
                pass

        temp_dic["nodes"]= new_node_list

        #write the modifed json file into the corresponding file listed in output_json_files
        with open(self.json_file, 'w') as outfile:
            json.dump(temp_dic, outfile, indent=4)
