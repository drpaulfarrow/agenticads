import openai
import os
from dotenv import load_dotenv

load_dotenv()
# Set your OpenAI API key directly here
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_recent_history(history_file="edge_history.txt", max_chars=4000):
    with open(history_file, "r", encoding="utf-8") as f:
        history = f.read()
        return history[-max_chars:]  # Only take the last 4000 characters

def ask_mebot(question, browsing_history_text):
    prompt = f"""
You are MeBot, an AI that knows the user's browsing history.

Browsing History:
{browsing_history_text}

User Question:
{question}

Answer:"""

    # No need to create client manually anymore – openai.api_key already set
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are MeBot, an AI that knows about the user's browsing history."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    print("\n🤖 MeBot's Response:\n")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    history = load_recent_history()

    while True:
        user_question = input("\nAsk MeBot a question about yourself (or type 'exit' to quit): ")
        if user_question.lower() in ("exit", "quit"):
            break
        ask_mebot(user_question, history)
