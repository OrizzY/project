import re
import math
import csv

# TEXT NORMALIZATION
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)

    stopwords = {
        'apa','apakah','yang','dan','di','ke','dari','berapa',
        'saya','kamu','kami','bisa','untuk','ya','dong',
        'tolong','mau','ingin','nih','itu','ini'
    }

    return [
        w for w in text.split()
        if w not in stopwords and len(w) > 2
    ]


# COSINE SIMILARITY
def cosine_similarity(vecA, vecB):
    dot = sum(vecA.get(k, 0) * vecB.get(k, 0) for k in vecA)
    magA = math.sqrt(sum(v * v for v in vecA.values()))
    magB = math.sqrt(sum(v * v for v in vecB.values()))
    return dot / (magA * magB) if magA and magB else 0



# TF-IDF ENGINE
def build_tfidf(documents):
    tf = []
    df = {}
    total_docs = len(documents)

    for doc in documents:
        words = normalize(doc)
        counts = {}

        for w in words:
            counts[w] = counts.get(w, 0) + 1

        doc_tf = {}
        for w, c in counts.items():
            doc_tf[w] = c / max(len(words), 1)
            df[w] = df.get(w, 0) + 1

        tf.append(doc_tf)

    tfidf = []
    for doc_tf in tf:
        doc_vec = {}
        for w, tf_val in doc_tf.items():
            idf = math.log(total_docs / df.get(w, 1))
            doc_vec[w] = tf_val * idf
        tfidf.append(doc_vec)

    return tfidf


# SEMANTIC FAQ MATCH
def semantic_faq_match(query, faqs, threshold=0.25):
    documents = [f['question'] for f in faqs]
    tfidf_docs = build_tfidf(documents)

    query_vec = {}
    for w in normalize(query):
        query_vec[w] = query_vec.get(w, 0) + 1

    best_score = 0
    best_index = None

    for i, doc_vec in enumerate(tfidf_docs):
        score = cosine_similarity(query_vec, doc_vec)
        if score > best_score:
            best_score = score
            best_index = i

    if best_score >= threshold:
        return faqs[best_index], best_score
    return None, best_score


# LOAD FAQ CSV
def load_dataset(path):
    data = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "question": row["Pertanyaan"],
                "answer": row["Jawaban"]
            })
    return data



# TESTING AKURASI
def test_accuracy(faqs, test_data, output_csv='hasil_uji.csv'):
    results = []
    correct = 0

    for row in test_data:
        query = row['query']
        expected = row['expected_answer']

        result, score = semantic_faq_match(query, faqs)
        predicted = result['answer'] if result else None

        is_correct = predicted == expected
        if is_correct:
            correct += 1

        results.append({
            'No': len(results) + 1,
            'Pertanyaan': query,
            'Jawaban Target': expected,
            'Jawaban Chatbot': predicted,
            'Score': round(score, 4),
            'Hasil': 'TRUE' if is_correct else 'FALSE'
})


    accuracy = correct / len(test_data)

    # simpan CSV buat laporan
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                'No',
                'Pertanyaan',
                'Jawaban Target',
                'Jawaban Chatbot',
                'Score',
                'Hasil'
            ]
        )
        writer.writeheader()
        writer.writerows(results)


    return accuracy

# load satu dataset
dataset = load_dataset(
    'data_test.csv'
)

# dataset sebagai FAQ (knowledge base)
faqs = dataset

# dataset sebagai data uji
test_data = [
    {
        "query": item["question"],
        "expected_answer": item["answer"]
    }
    for item in dataset
]

accuracy = test_accuracy(faqs, test_data)

print(f"Akurasi chatbot: {accuracy * 100:.2f}%")


