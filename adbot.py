import openai
import random
import os

# Create OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def load_random_campaigns(campaign_file="campaign_data.txt", num_campaigns=100):
    with open(campaign_file, "r", encoding="utf-8") as f:
        campaigns = f.read().split("\n\n")  # Assuming each campaign is separated by two newlines
        sample_campaigns = random.sample(campaigns, min(num_campaigns, len(campaigns)))
        return "\n\n".join(sample_campaigns)

def ask_adbot(question, campaigns_text):
    prompt = f"""
You are AdBot, an AI assistant who knows about advertising campaigns.

Here are 100 campaigns:

{campaigns_text}

Please find the 3 best matching campaigns based on this user question:

{question}

Only list the 3 most relevant campaigns with their Campaign Name, Brand, Category, Budget, Flight Dates, Target CPM, and Target CPA.

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4" if you prefer
        messages=[
            {"role": "system", "content": "You are AdBot, an AI assistant who knows about advertising campaigns and helps pick the best matching ones."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500  # Allow enough room for 3 campaigns
    )

    print("\n🤖 AdBot's Response:\n")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    while True:
        campaigns_text = load_random_campaigns()
        user_question = input("\nAsk AdBot a question about campaigns (or type 'exit' to quit): ")
        if user_question.lower() in ("exit", "quit"):
            break
        ask_adbot(user_question, campaigns_text)
