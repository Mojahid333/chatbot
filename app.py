from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np

app = Flask(__name__)

print("Loading AI model... please wait...")
model = SentenceTransformer('all-MiniLM-L6-v2')

with open("college_data.json", "r") as f:
    data = json.load(f)

print("Loading your questions into memory...")
questions = [item["question"] for item in data]
answers = [item["answer"] for item in data]
question_embeddings = model.encode(questions)

print("✅ System Ready! All questions loaded.")

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    query_embedding = model.encode([user_question])
    similarities = cosine_similarity(query_embedding, question_embeddings)[0]
    best_match = int(np.argmax(similarities))
    answer = answers[best_match]
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

