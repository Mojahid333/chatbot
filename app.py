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
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

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

def send_email(question, answer):
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "onboarding@resend.dev",
                "to": "mojahid8330206@gmail.com",
                "subject": "Chatbot Unsatisfied Answer Alert!",
                "text": f"""A student was NOT satisfied with the chatbot answer!

Question: {question}

Answer Given: {answer}

Please update the JSON file accordingly."""
            }
        )
        print(f"Email response: {response.status_code} {response.text}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

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

@app.route('/feedback', methods=['POST'])
def feedback():
    question = request.json.get("question", "")
    answer = request.json.get("answer", "")
    satisfied = request.json.get("satisfied", True)
    
    if not satisfied:
        email_thread = threading.Thread(target=send_email, args=(question, answer))
        email_thread.daemon = True
        email_thread.start()
        return jsonify({"status": "Email sent!"})
    
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)