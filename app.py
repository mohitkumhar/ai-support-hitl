from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymongo
import os
from dotenv import load_dotenv
from app.utils import (
    move_pending_ticket_to_completed_in_db,
    move_drafted_ticket_to_completed_in_db,
    move_escalated_ticket_to_completed_in_db,
    call_llm_to_rephase,
    move_tickets_to_escalated_tickets_in_db,
    fetch_similar_past_tickets,
    fetch_similar_policy
)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
try:
    client = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
    db = client["ai_support_system"]
    
    # Collections
    pending_tickets_collection = db["pending_tickets"]
    ai_pending_drafted_tickets = db["ai_pending_drafted_tickets"]
    solved_tickets_collection = db["solved_tickets"]
    escalated_tickets_collection = db["escalated_tickets"]
except Exception as e:
    print(f"Database connection error: {e}")

@app.route("/")
def home():
    """Home page route."""
    return render_template("index.html")

def _prepare_tickets(cursor):
    tickets = list(cursor)
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])
    return tickets

@app.route("/pending")
def pending_tickets():
    tickets = _prepare_tickets(pending_tickets_collection.find().limit(20))
    return render_template("tickets.html", title="Pending Tickets", queue="pending", tickets=tickets)

@app.route("/drafted")
def drafted_tickets():
    tickets = _prepare_tickets(ai_pending_drafted_tickets.find().limit(20))
    return render_template("tickets.html", title="Drafted Tickets", queue="drafted", tickets=tickets)

@app.route("/escalated")
def escalated_tickets():
    tickets = _prepare_tickets(escalated_tickets_collection.find().limit(20))
    return render_template("tickets.html", title="Escalated Tickets", queue="escalated", tickets=tickets)

@app.route("/completed")
def completed_tickets():
    tickets = _prepare_tickets(solved_tickets_collection.find().limit(20))
    return render_template("tickets.html", title="Completed Tickets", queue="completed", tickets=tickets)

@app.route("/action", methods=["POST"])
def ticket_action():
    """Handle different actions on tickets (resolve, escalate, rephrase)"""
    action = request.form.get("action")
    ticket_id = request.form.get("ticket_id")
    reply = request.form.get("reply", "")
    queue = request.form.get("queue")
    temperature = request.form.get("temperature", 0.5)

    if not ticket_id:
        return "Invalid Request", 400

    try:
        temperature = float(temperature)
    except:
        temperature = 0.5

    if action == "resolve":
        if queue == "pending":
            move_pending_ticket_to_completed_in_db(ticket_id, reply)
        elif queue == "drafted":
            move_drafted_ticket_to_completed_in_db(ticket_id, reply)
        elif queue == "escalated":
            move_escalated_ticket_to_completed_in_db(ticket_id, reply)
        return redirect(url_for(f'{queue}_tickets'))

    elif action == "escalate":
        col_map = {
            "pending": "pending_tickets",
            "drafted": "ai_pending_drafted_tickets"
        }
        if queue in col_map:
            move_tickets_to_escalated_tickets_in_db(ticket_id, col_map[queue])
        return redirect(url_for(f'{queue}_tickets'))

    elif action == "rephrase":
        if reply.strip():
            rephrased = call_llm_to_rephase(reply, temperature)
            # Re-render same page but with rephrased text injected
            return jsonify({"rephrased_text": rephrased})
        return jsonify({"error": "No text to rephrase"})

    return redirect(url_for('home'))

@app.route("/similar", methods=["GET"])
def similar_data():
    ticket_issue = request.args.get("issue", "")
    if not ticket_issue:
        return jsonify({"past_tickets": [], "policies": []})
        
    past = fetch_similar_past_tickets(ticket_issue, os.getenv("OPEN_AI_KEY"))
    policies = fetch_similar_policy(ticket_issue, os.getenv("OPEN_AI_KEY"))
    
    # parse the tuples returning from chromadb
    past_clean = [{"content": doc.page_content, "score": score} for doc, score in past]
    policies_clean = [{"content": doc.page_content, "score": score} for doc, score in policies]

    return jsonify({"past_tickets": past_clean, "policies": policies_clean})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

