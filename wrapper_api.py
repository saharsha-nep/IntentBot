from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

RASA_URL = "http://localhost:5005/model/parse" #Change according to server needs

class TextInput(BaseModel):
    text: str

@app.post("/nlu/parse")
def parse_text(input_data: TextInput):
    response = requests.post(RASA_URL, json={"text": input_data.text})
    rasa_data = response.json()

    output = {
        "intent": rasa_data["intent"]["name"],
        "entities": {e["entity"]: e["value"] for e in rasa_data.get("entities", [])},
        "original_text": rasa_data["text"]
    }

    return output
