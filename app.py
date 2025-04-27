from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import mebot_adbot
import logging
import os

# ========== Logging Setup ==========
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ========== Flask Setup ==========
app = Flask(__name__)
# Use filesystem session storage
app.config["SESSION_TYPE"] = "filesystem"  # Could also use 'redis', 'memcached', etc.

# Initialize the session system
Session(app)

# ========== Route: Home ==========
@app.route("/")
def index():
    session.clear()
    logging.info("Starting new session.")
    return render_template("index.html")

# ========== Route: Step-by-Step Conversation ==========
@app.route("/step", methods=["POST"])
def step():
    if "step" not in session:
        # First time initializing
        session["step"] = 0
        session["history"] = mebot_adbot.load_recent_history()
        session["campaigns_text"] = mebot_adbot.load_random_campaigns()
        session["interests"] = ""
        session["initial_campaigns"] = ""
        session["review"] = ""

    step = session["step"]
    message = None

    # 🔥 FIX: Stop when all steps are done
    if step > 8:
        logging.info("Conversation finished.")
        return jsonify({"done": True})

    if step == 0:
        message = "👤 MeBot: Analyzing your browsing history..."

    elif step == 1:
        interests = mebot_adbot.get_user_interests(session["history"])
        session["interests"] = interests
        message = f"🎯 MeBot found interests: <strong>{interests}</strong>"

    elif step == 2:
        # Fake step where MeBot is moved to a trusted execution environment
        message = "👤 MeBot: Moving into a trusted execution environment to interact with AdBot... Please hold on."

    elif step == 3:
        message = "🤖 AdBot: Selecting campaigns..."

    elif step == 4:
        initial_campaigns = mebot_adbot.get_matching_campaigns(session["interests"], session["campaigns_text"])
        session["initial_campaigns"] = initial_campaigns
        message = f"📋 AdBot's Initial Picks:<br><pre>{initial_campaigns}</pre>"

    elif step == 5:
        message = "👤 MeBot: Reviewing AdBot's picks..."

    elif step == 6:
        review = mebot_adbot.mebot_review_campaigns(session["interests"], session["initial_campaigns"])
        session["review"] = review
        message = f"🧠 MeBot's Review:<br>{review}"

    elif step == 7:
        if "Needs Improvement" in session["review"]:
            message = "♻️ AdBot: Refining campaigns based on MeBot feedback..."
        else:
            message = "✅ AdBot: Initial picks were good! 🎯"

    elif step == 8:
        if "Needs Improvement" in session["review"]:
            refined_campaigns = mebot_adbot.adbot_refine_campaigns(
                session["interests"], session["initial_campaigns"], session["campaigns_text"]
            )
            message = f"✅ AdBot's Final Picks:<br><pre>{refined_campaigns}</pre>"
        else:
            message = None

    session["step"] += 1  # move to the next step!

    logging.info(f"Completed step {step}. Moving to step {session['step']}...")

    return jsonify({
        "message": message,
        "done": False
    })

# ========== Run ==========
if __name__ == "__main__":
    logging.info("Starting Flask app...")
    app.run(debug=True, use_reloader=True)
