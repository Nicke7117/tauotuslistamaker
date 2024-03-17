import json

class Config:
    def load_json(self):
        with open('config.json') as json_file:
            data = json.load(json_file)
            return data
        
        