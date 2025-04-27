import openai
import os
import random

openai.api_key = os.getenv("OPENAI_API_KEY")

# ========== Loaders ==========
def load_recent_history(history_file="edge_history.txt", max_chars=8000):
    with open(history_file, "r", encoding="utf-8") as f:
        history = f.read()
        return history[-max_chars:]

def load_random_campaigns(campaign_file="campaign_data.txt", num_campaigns=100):
    with open(campaign_file, "r", encoding="utf-8") as f:
        campaigns = f.read().split("\n\n")
        sample_campaigns = random.sample(campaigns, min(num_campaigns, len(campaigns)))
        return "\n\n".join(sample_campaigns)

# ========== Agents ==========
def get_user_interests(history_text):
    prompt = f"""
You are MeBot. Based on the user's browsing history, write a detailed summary of what kind of things the user is interested in and make predictions about what kind of things they might buy.

Browsing History:
{history_text}
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are MeBot, expert in analyzing browsing history to detect interests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    interests = response.choices[0].message.content.strip()
    return interests

def get_matching_campaigns(interests, campaigns_text):
    prompt = f"""
You are AdBot. You know about 100 advertising campaigns.

Here are the campaigns:
{campaigns_text}

The user is interested in: {interests}.

Pick 3 campaigns that best match these interests. List each campaign clearly.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are AdBot, matching users to ad campaigns."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

def mebot_review_campaigns(interests, selected_campaigns):
    prompt = f"""
You are MeBot. The user is interested in: {interests}.

Here are the campaigns AdBot selected:
{selected_campaigns}

Please review:
- Are the campaigns relevant?
- Are any missing key user interests?
- Answer with "Good Match" or "Needs Improvement" and a short explanation.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are MeBot, reviewing how well ad campaigns match user interests."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def adbot_refine_campaigns(interests, previous_selection, campaigns_text):
    prompt = f"""
You are AdBot again. Your previous selection was:

{previous_selection}

MeBot said it needs improvement.

Please refine your selection:
- Focus more carefully on matching the user's interests: {interests}.
- Replace campaigns if necessary.
- Return exactly 3 improved campaigns.
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are AdBot refining your campaign selection based on MeBot feedback."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

# ========== Main Program ==========
if __name__ == "__main__":
    print("\n🚀 Welcome to the Agentic Ad Selector (Conversational Mode)!\n")

    history = load_recent_history()
    campaigns_text = load_random_campaigns()

    # Step 1: MeBot predicts interests
    print("🤖 MeBot is analyzing your browsing history...")
    interests = get_user_interests(history)
    print(f"\n🎯 Detected Interests: {interests}\n")

    # Step 2: AdBot picks initial campaigns
    print("🤖 AdBot is selecting campaigns...")
    initial_campaigns = get_matching_campaigns(interests, campaigns_text)
    print("\n📋 Initial AdBot Picks:\n")
    print(initial_campaigns)

    # Step 3: MeBot reviews the campaigns
    print("\n🔎 MeBot is reviewing AdBot's picks...")
    review = mebot_review_campaigns(interests, initial_campaigns)
    print("\n🧠 MeBot's Review:\n")
    print(review)

    if "Needs Improvement" in review:
        print("\n♻️ AdBot is refining the campaign selection based on feedback...")
        refined_campaigns = adbot_refine_campaigns(interests, initial_campaigns, campaigns_text)
        print("\n✅ Final AdBot Picks (after refinement):\n")
        print(refined_campaigns)
    else:
        print("\n✅ Initial picks were good! No refinement needed.")

    print("\n🎉 Done!")
