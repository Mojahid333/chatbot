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

qa_context = ""
for item in data:
    qa_context += f"Q: {item['question']}\nA: {item['answer']}\n\n"

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

    prompt = f"""You are a college chatbot. Answer the student's question using ONLY the information provided below. Give a direct short answer only.

{qa_context}

Student question: {user_question}

Answer:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            }
        )
        answer = response.json()["choices"][0]["message"]["content"]
        return jsonify({"answer": answer.strip()})
    except:
        return jsonify({"answer": "Sorry, please try again."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)