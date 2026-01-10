"""
    This is the Sample ticket data generation file, for testing purposes.
"""

import os
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()


# 1. Setup MongoDB Connection
# client = MongoClient(os.getenv("MONGO_URI"))
client = MongoClient("mongodb://localhost:27017/")
db = client["ai_support_system"]

# Collection definitions
pending_col = db["pending_tickets"]
drafted_col = db["ai_pending_drafted_tickets"]
solved_col = db["solved_tickets"]
escalated_col = db["escalated_tickets"]  # New collection for escalated data

base_time = datetime.datetime(2025, 12, 30, 9, 0, 0)

# --- DATA GENERATION ---

# 1. PENDING DATA (TKT_0001 to TKT_0010)
pending_data = []
for i in range(1, 11):
    pending_data.append({
        'ticket_id': f"TKT_{i:04d}",
        'issue': f"Network connectivity issue reported by user {i}",
        'used_policy': "Standard Network Protocol",
        'metadata': {
            'ticket_creation_time':
                base_time + datetime.timedelta(minutes=i*10),
            'category': "Technical",
            'priority': 'medium',
            'is_drafted': False
        }
    })

# 2. DRAFTED DATA (TKT_0011 to TKT_0020)
drafted_data = []
for i in range(11, 21):
    drafted_data.append({
        'ticket_id': f"TKT_{i:04d}",
        'issue': f"Request for account upgrade - Tier {i-10}",
        'used_policy': "Subscription Upgrade Policy",
        'ai_drafted_response':
            "Your account upgrade request has been processed successfully.",
        'used_reference_ticket_id': f"TKT_{i-10:04d}",
        'confidence': 0.88,
        'metadata': {
            'ticket_creation_time': base_time + datetime.timedelta(minutes=i*12),
            'category': "Billing",
            'priority': 'high',
            'is_drafted': True,
            'tone': "Professional"
        }
    })

# 3. SOLVED DATA (TKT_0021 to TKT_0030)
solved_data = []
for i in range(21, 31):
    creation_time = base_time + datetime.timedelta(minutes=i*15)
    solved_data.append({
        'ticket_id': f"TKT_{i:04d}",
        'issue': f"Hardware failure report #{i}",
        'resolution': "Replacement unit shipped and tracking number provided.",
        'ai_drafted_response':
            "We have processed your replacement. Your tracking ID is XYZ.",
        'used_policy': "Hardware Warranty Policy",
        'used_reference_ticket_id': "REF_GLOBAL_01",
        'confidence': 0.95,
        'metadata': {
            'ticket_creation_time': creation_time,
            'ticket_closure_time': creation_time + datetime.timedelta(hours=2),
            'category': "Hardware",
            'priority': 'medium',
            'is_drafted': True,
            'tone': "Helpful"
        }
    })

# 4. ESCALATED DATA (TKT_0031 to TKT_0040)
escalated_data = []
for i in range(31, 41):
    escalated_data.append({
        'ticket_id': f"TKT_{i:04d}",
        'issue': f"Urgent security breach or payment failure reported by VIP user {i}",
        'used_policy': "Critical Escalation Protocol",
        'ai_drafted_response':
            "This ticket is Escalated. A senior manager is reviewing your case.",
        'used_reference_ticket_id': f"TKT_{i-20:04d}",
        'confidence': 0.65,  # Usually lower confidence for escalated items
        'metadata': {
            'ticket_creation_time': base_time + datetime.timedelta(minutes=i*8),
            'category': "Security",
            'priority': 'critical',
            'is_drafted': True,
            'escalation_reason': "High priority / Complexity"
        }
    })


# --- DATABASE INSERTION ---


def upload_data():
    """
    This Function uploads the generated sample data
    to MongoDB collections.
    The Generated Data includes:
    1. Pending Tickets
    2. AI Drafted Tickets
    3. Solved Tickets
    4. Escalated Tickets
    """
    try:
        # Clear existing test data
        pending_col.delete_many({})
        drafted_col.delete_many({})
        solved_col.delete_many({})
        escalated_col.delete_many({})

        if pending_data:
            pending_col.insert_many(pending_data)
        if drafted_data:
            drafted_col.insert_many(drafted_data)
        if solved_data:
            solved_col.insert_many(solved_data)
        if escalated_data:
            escalated_col.insert_many(escalated_data)

        total_docs = len(pending_data) + len(drafted_data) + len(solved_data) + len(escalated_data)

        print(f"""✅ Success: {total_docs} documents successfully uploaded.""")
    except ConnectionFailure as e:
        print(f"❌ Error uploading data: {e}")


if __name__ == "__main__":
    upload_data()
