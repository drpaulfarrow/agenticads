import openai
import os
import random
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ========== Load recent browsing history ==========
def load_recent_history(history_file="edge_history.txt", max_chars=4000):
    with open(history_file, "r", encoding="utf-8") as f:
        history = f.read()
        return history[-max_chars:]

# ========== Load random campaigns ==========
def load_random_campaigns(campaign_file="campaign_data.txt", num_campaigns=100):
    with open(campaign_file, "r", encoding="utf-8") as f:
        campaigns = f.read().split("\n\n")
        sample_campaigns = random.sample(campaigns, min(num_campaigns, len(campaigns)))
        return "\n\n".join(sample_campaigns)

# ========== Ask MeBot for interests ==========
def ask_mebot_for_interests(browsing_history_text):
    prompt = f"""
You are MeBot, an AI that knows the user's browsing history.

Browsing History:
{browsing_history_text}

Based on this browsing history, what are 1 to 3 advertising categories this user might be interested in? Examples of categories: technology, travel, fashion, gaming, fitness, finance, education.

Only list the categories in a short comma-separated list. (Example: "Technology, Fitness, Travel")
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are MeBot, an AI that predicts user interests based on browsing history."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=100
    )

    interests = response.choices[0].message.content.strip()
    return interests

# ========== Ask AdBot for matching campaigns ==========
def ask_adbot_for_campaigns(interests, campaigns_text):
    prompt = f"""
You are AdBot, an AI assistant who knows about advertising campaigns.

Here are 100 campaigns:

{campaigns_text}

The user is interested in the following categories: {interests}.

Find the 3 best matching campaigns for the user based on their interests.

Only list the 3 most relevant campaigns with their Campaign Name, Brand, Category, Budget, Flight Dates, Target CPM, and Target CPA.

Answer:"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are AdBot, an AI assistant who matches users to ad campaigns."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

# ========== Main program ==========
if __name__ == "__main__":
    print("\n🚀 Welcome to the Agentic Ad Selector (MeBot + AdBot)!\n")

    history = load_recent_history()
    campaigns_text = load_random_campaigns()

    # Step 1: Ask MeBot for user interests
    print("🤖 Asking MeBot for your interests based on browsing history...")
    interests = ask_mebot_for_interests(history)
    print(f"\n🎯 MeBot thinks you're interested in: {interests}")

    # Step 2: Ask AdBot for matching campaigns
    print("\n🤖 Asking AdBot to find matching ad campaigns...")
    campaigns = ask_adbot_for_campaigns(interests, campaigns_text)

    print("\n✅ Here are 3 ad campaigns selected for you:\n")
    print(campaigns)

    print("\n🎉 Thank you for using the Agentic Ad Selector!")
