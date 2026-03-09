from flask import Flask, request, jsonify
import json
import requests
import threading
import time
import os

app = Flask(__name__)

with open("college_data.json", "r") as f:
    data = json.load(f)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def keep_alive():
    while True:
        time.sleep(600)
        try:
            requests.get("https://chatbot-8uvt.onrender.com")
        except:
            pass

thread = threading.Thread(target=keep_alive)
thread.daemon = True
thread.start()

@app.route('/', methods=['GET'])
def home():
    return "Chatbot is running!"

@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    
    user_q_lower = user_question.lower()
    user_words = set(user_q_lower.split())
    scores = []
    for i, item in enumerate(data):
        q_lower = item['question'].lower()
        q_words = set(q_lower.split())
        word_score = len(user_words & q_words)
        substring_bonus = 5 if any(word in q_lower for word in user_words if len(word) > 3) else 0
        score = word_score + substring_bonus
        scores.append((score, i))
    
    scores.sort(reverse=True)
    top10 = scores[:10]
    
    small_context = ""
    for score, i in top10:
        small_context += f"Q: {data[i]['question']}\nA: {data[i]['answer']}\n\n"

    prompt = f"""Answer this student question using ONLY the info below. Be very brief.

{small_context}

Question: {user_question}
Answer:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100
            },
            timeout=10
        )
        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": answer.strip()})
    except:
        return jsonify({"answer": "Sorry, please try again."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)