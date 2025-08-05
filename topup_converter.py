import yaml
import re

def str_presenter(dumper, data):
    if '\n' in data:
        data = data.rstrip('\n')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def text_to_rasa_nlu_append(txt_file, nlu_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    examples = []
    for line in lines:
        new_line = re.sub(r'(\d+)', r'[\1](amount)', line, count=1)
        examples.append(f"- {new_line}")

    new_examples_text = "\n".join(examples).rstrip('\n') 

    with open(nlu_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    nlu_list = data.get("nlu", [])
    topup_intent = None
    for intent in nlu_list:
        if intent.get("intent") == "topup":
            topup_intent = intent
            break
    if not topup_intent:
        topup_intent = {"intent": "topup", "examples": ""}
        nlu_list.append(topup_intent)

    if topup_intent.get("examples"):
        existing = topup_intent["examples"].rstrip('\n')
        topup_intent["examples"] = existing + "\n" + new_examples_text
    else:
        topup_intent["examples"] = new_examples_text

    data["nlu"] = nlu_list

    with open(nlu_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

if __name__ == "__main__":
    text_to_rasa_nlu_append("topup_examples.txt", "data/nlu.yml")
