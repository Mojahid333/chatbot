@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    
    # Find top 5 matching questions first
    user_words = set(user_question.lower().split())
    scores = []
    for i, item in enumerate(data):
        q_words = set(item['question'].lower().split())
        score = len(user_words & q_words)
        scores.append((score, i))
    
    scores.sort(reverse=True)
    top5 = scores[:5]
    
    # Build small context with only top 5
    small_context = ""
    for score, i in top5:
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
