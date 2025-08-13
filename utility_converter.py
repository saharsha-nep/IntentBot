import yaml
import re

# Editable list of utilities (all lowercase for consistency)
utilities = ["water", "electricity", "internet", "insurance"]

def str_presenter(dumper, data):
    if '\n' in data:
        data = data.rstrip('\n')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def annotate_entities(line):
    line = re.sub(r'(\d+)', r'[\1](amount)', line)

    # Match utilities case-insensitively, replace with lowercase
    for util in utilities:
        pattern = rf"\b({util})\b"
        line = re.sub(
            pattern,
            f"[{util}](utility)",  # always lowercase
            line,
            flags=re.IGNORECASE
        )
    return line

def normalize_example(text):
    """Replace entity values with placeholders for duplicate detection."""
    text = re.sub(r'\[\d+\]\(amount\)', '[AMOUNT](amount)', text)
    for util in utilities:
        text = re.sub(rf'\[{util}\]\(utility\)', '[UTILITY](utility)', text, flags=re.IGNORECASE)
    return text.lower().strip()

def text_to_rasa_nlu_append(txt_file, nlu_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    new_examples = [f"- {annotate_entities(line)}" for line in lines]

    with open(nlu_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    nlu_list = data.get("nlu", [])
    pay_intent = None
    for intent in nlu_list:
        if intent.get("intent") == "pay_utility":
            pay_intent = intent
            break
    if not pay_intent:
        pay_intent = {"intent": "pay_utility", "examples": ""}
        nlu_list.append(pay_intent)

    if pay_intent.get("examples"):
        existing_lines = [line.strip() for line in pay_intent["examples"].split("\n") if line.strip()]
    else:
        existing_lines = []

    normalized_existing = {normalize_example(e) for e in existing_lines}

    unique_new = []
    for ex in new_examples:
        if normalize_example(ex) not in normalized_existing:
            unique_new.append(ex)
            normalized_existing.add(normalize_example(ex))

    if existing_lines:
        pay_intent["examples"] = "\n".join(existing_lines + unique_new)
    else:
        pay_intent["examples"] = "\n".join(unique_new)

    data["nlu"] = nlu_list

    with open(nlu_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

if __name__ == "__main__":
    text_to_rasa_nlu_append("utility_examples.txt", "data/nlu.yml")
