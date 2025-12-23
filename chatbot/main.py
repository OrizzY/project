import json
import os
import re
import csv
from test_data import test_cases
from rapidfuzz import process, fuzz

FILE_NAME = "rules.json"
THRESHOLD = 70

# Load rules
if os.path.exists(FILE_NAME):
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        rules = json.load(f)
else:
    rules = {}

def save_rules():
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)

def add_new_rule():
    intent = input("Nama intent: ").lower()
    pattern = input("Pertanyaan: ").lower()
    response = input("Jawaban chatbot: ")

    new_data = {
        "pattern": pattern,
        "response": response
    }

    if intent in rules:
        rules[intent].append(new_data)
        print("Pattern & response ditambahkan ke intent lama 😄")
    else:
        rules[intent] = [new_data]
        print("Intent baru ditambahkan 😄")

    save_rules()

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
        return best_response

    return "Maaf aku belum paham 😅"

def evaluate_chatbot_to_csv(test_cases, filename="hasil_uji.csv"):
    correct = 0
    total = len(test_cases)

    rows = []

    for i, test in enumerate(test_cases, start=1):
        question = test["question"]
        expected = test["expected"]
        bot_answer = chatbot_response(question)

        is_correct = bot_answer == expected
        if is_correct:
            correct += 1

        rows.append([
            i,
            question,
            bot_answer,
            expected,
            "TRUE" if is_correct else "FALSE"
        ])

    accuracy = (correct / total) * 100

    # Simpan ke CSV
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "No",
            "Pertanyaan",
            "Jawaban Chatbot",
            "Jawaban Diharapkan",
            "Hasil"
        ])
        writer.writerows(rows)

    print("Pengujian selesai 💀")
    print(f"Total pertanyaan : {total}")
    print(f"Jawaban benar    : {correct}")
    print(f"Akurasi          : {accuracy:.2f}%")
    print(f"Hasil disimpan di file: {filename}")

evaluate_chatbot_to_csv(test_cases)

print("Chatbot aktif!")
print("Ketik:")
print("- 'tambah' → tambah pertanyaan & jawaban")
print("- 'keluar' → exit\n")

while True:
    user_input = input("Kamu: ")

    if user_input.lower() == "keluar":
        print("Bot: Sampai jumpa 👋")
        break

    if user_input.lower() == "tambah":
        add_new_rule()
        continue

    print("Bot:", chatbot_response(user_input))
