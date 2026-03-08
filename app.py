from flask import Flask, request, jsonify
import json
import requests
import threading
import time

app = Flask(__name__)

with open("college_data.json", "r") as f:
    data = json.load(f)

GEMINI_API_KEY = "AIzaSyC9w_cxhJ3plFU6sa-wBorQuzB71o7aYZg"

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
    
    prompt = f"""You are a college chatbot. Answer the student's question using ONLY the information provided below. Give a direct, short answer.

{qa_context}

Student question: {user_question}

Give only the answer, nothing else."""

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )
        answer = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"answer": answer.strip()})
    except:
        return jsonify({"answer": "Sorry, please try again."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)