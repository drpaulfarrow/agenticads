import openai
import random
import logging
from datetime import datetime, timedelta
import concurrent.futures
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate a batch of campaigns
def generate_campaign_details_batch(batch_size):
    prompt = f"""
    Generate {batch_size} campaigns with the following details for each:
    - A unique and creative Brand Name
    - A relevant Campaign Category
    - A short and appealing Description (max 3 sentences) that highlights the brand's strengths.

    Format exactly like this for each campaign:
    Brand Name: <brand>
    Campaign Category: <category>
    Description: <description>

    Separate each campaign clearly.
    """

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,  # Safe for 10-15 campaigns
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    campaigns_raw = content.split("\n\n")

    campaigns = []
    for raw in campaigns_raw:
        lines = raw.strip().split("\n")
        if len(lines) >= 3:
            brand = lines[0].replace("Brand Name: ", "").strip()
            category = lines[1].replace("Campaign Category: ", "").strip()
            description = lines[2].replace("Description: ", "").strip()
            campaigns.append((brand, category, description))

    return campaigns

# Main function
def generate_campaigns(total_campaigns=100, batch_size=10, output_file="campaign_data.txt", max_workers=3, request_delay=2):
    today = datetime.today()

    campaigns_needed = total_campaigns
    all_campaigns = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while campaigns_needed > 0:
            batch = min(batch_size, campaigns_needed)
            future = executor.submit(generate_campaign_details_batch, batch)
            futures.append(future)
            campaigns_needed -= batch

            logging.info(f"🔵 Launched a batch request. Sleeping {request_delay}s to avoid rate limit...")
            time.sleep(request_delay)  # <-- Add a little sleep between launches

        logging.info(f"🔵 Launched {len(futures)} batch requests (max {max_workers} concurrent)...")

        for future in concurrent.futures.as_completed(futures):
            try:
                batch_result = future.result()
                all_campaigns.extend(batch_result)
                logging.info(f"✅ One batch completed with {len(batch_result)} campaigns.")
            except Exception as e:
                logging.error(f"❌ Batch failed: {e}")

    logging.info(f"🔵 Writing {len(all_campaigns)} campaigns to file...")

    with open(output_file, "w", encoding="utf-8") as f:
        for i, (brand, category, description) in enumerate(all_campaigns, 1):
            budget = random.randint(5000, 100000)
            start_date = today + timedelta(days=random.randint(-30, 30))
            end_date = start_date + timedelta(days=random.randint(7, 60))
            target_cpm = round(random.uniform(1.5, 10.0), 2)
            target_cpa = round(random.uniform(5.0, 50.0), 2)

            f.write(f"Campaign Name: {brand} {category} Campaign {i}\n")
            f.write(f"Brand: {brand}\n")
            f.write(f"Category: {category}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Budget: {budget}\n")
            f.write(f"Flight Dates: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n")
            f.write(f"Target CPM: {target_cpm}\n")
            f.write(f"Target CPA: {target_cpa}\n")
            f.write("\n")

    logging.info(f"🎉 Finished writing {len(all_campaigns)} campaigns into {output_file}")

if __name__ == "__main__":
    generate_campaigns(
        total_campaigns=100, 
        batch_size=10, 
        max_workers=1,       # Only one request happening at a time
        request_delay=22     # Wait 22 seconds between each request
    )