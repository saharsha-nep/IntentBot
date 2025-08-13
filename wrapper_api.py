from fastapi import FastAPI
from pydantic import BaseModel
import requests
from collections import defaultdict

app = FastAPI()

RASA_URL = "http://localhost:5005/model/parse"  # Change as needed

class TextInput(BaseModel):
    text: str

@app.post("/nlu/parse")
def parse_text(input_data: TextInput):
    response = requests.post(RASA_URL, json={"text": input_data.text})
    rasa_data = response.json()

    entities_grouped = defaultdict(list)
    for e in rasa_data.get("entities", []):
        entities_grouped[e["entity"]].append(e["value"])

    return {
        "intent": rasa_data["intent"]["name"],
        "entities": dict(entities_grouped),
        "original_text": rasa_data["text"]
    }
