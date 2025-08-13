import yaml
import re

def str_presenter(dumper, data):
    if '\n' in data:
        data = data.rstrip('\n')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def normalize_example(text):
    """Remove entity values for duplicate detection (amounts replaced with placeholder)."""
    # Replace numbers with a standard placeholder for comparison
    text_no_amount = re.sub(r'\[\d+\]\(amount\)', '[AMOUNT](amount)', text)
    return text_no_amount.lower().strip()

def text_to_rasa_nlu_append(txt_file, nlu_file):
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Convert new lines
    new_examples = []
    for line in lines:
        # Tag first number as amount
        tagged = re.sub(r'(\d+)', r'[\1](amount)', line, count=1)
        new_examples.append(f"- {tagged}")

    # Load YAML
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

    # Get existing examples and normalize for duplicate detection
    if topup_intent.get("examples"):
        existing_lines = [line.strip() for line in topup_intent["examples"].split("\n") if line.strip()]
    else:
        existing_lines = []

    normalized_existing = {normalize_example(e) for e in existing_lines}

    # Filter out new examples that are duplicates ignoring amounts
    unique_new = []
    for ex in new_examples:
        if normalize_example(ex) not in normalized_existing:
            unique_new.append(ex)
            normalized_existing.add(normalize_example(ex))

    # Append only unique examples
    if existing_lines:
        topup_intent["examples"] = "\n".join(existing_lines + unique_new)
    else:
        topup_intent["examples"] = "\n".join(unique_new)

    data["nlu"] = nlu_list

    # Write YAML
    with open(nlu_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)

if __name__ == "__main__":
    text_to_rasa_nlu_append("topup_examples.txt", "data/nlu.yml")
