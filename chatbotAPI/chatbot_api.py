from flask import Flask, request, jsonify
import json
import re
from rapidfuzz import fuzz

app = Flask(__name__)

with open("rules.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def chatbot_response(user_input):
    user_input = clean_text(user_input)
    best_score = 0
    best_response = None

    for intent in rules.values():
        for item in intent:
            pattern = clean_text(item["pattern"])
            score = fuzz.token_set_ratio(user_input, pattern)

            if score > best_score:
                best_score = score
                best_response = item["response"]
        
    if best_score >= 70:
        return best_response, best_score
    
    return "Maaf aku belum paham", best_score

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    massage = data.get("massage", "")

    reply, score = chatbot_response(massage)

    return jsonify({
        "reply": reply,
        "confidence": score / 100
    })

if __name__ == "__main__":
    app.run(debug=True)