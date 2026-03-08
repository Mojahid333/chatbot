from flask import Flask, request, jsonify
import json

app = Flask(__name__)

with open("college_data.json", "r") as f:
    data = json.load(f)

questions = [item["question"].lower() for item in data]
answers = [item["answer"] for item in data]

def find_answer(user_q):
    user_q = user_q.lower()
    user_words = set(user_q.split())
    best_score = -1
    best_index = 0
    for i, q in enumerate(questions):
        q_words = set(q.split())
        score = len(user_words & q_words)
        if score > best_score:
            best_score = score
            best_index = i
    return answers[best_index]
@app.route('/', methods=['GET'])
def home():
    return "Chatbot is running!"
@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    answer = find_answer(user_question)
    return jsonify({"answer": answer})
import threading
import requests
import time

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
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
