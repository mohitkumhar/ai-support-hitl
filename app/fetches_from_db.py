"""
Module to fetch tickets from the database,
draft responses using LLM, and save drafts back to the database.
"""

import os
import time
from typing import Optional

from dotenv import load_dotenv

import pymongo
from pymongo.errors import ConnectionFailure

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from response_drafting_utils import ResponseDraftingOutput
from app.utils import (
        get_embedding_model,
        connect_policy_vectordb,
        connect_previous_record_vector_db,
        get_llm_object
    )

load_dotenv()

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

#  connecting to DB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["ai_support_system"]

pending_tickets_collection = db["pending_tickets"]
draft_tickets_collection = db['draft_tickets']


# creating embedding model object
embeddings = get_embedding_model(open_ai_key=OPEN_AI_KEY)
llm = get_llm_object(open_ai_key=OPEN_AI_KEY)

# connecting to vector DB Chroma
policy_vector_db = connect_policy_vectordb(open_ai_key=OPEN_AI_KEY)
previous_record_vector_db = connect_previous_record_vector_db(open_ai_key=OPEN_AI_KEY)


def response_drafting(
            ticket_id: str,
            query: str,
            policy: Optional[str] = None,
            previous_record: Optional[tuple] = None
        ) -> ResponseDraftingOutput:
    """
    Generate a drafted response for a customer support ticket using LLM.

    Args:
        ticket_id (str): The unique identifier of the ticket.
        query (str): The customer's issue or query.
        policy (Optional[str]): The relevant policy to be followed.
        previous_record (Optional[tuple]): Previous resolved tickets for reference.

    Returns:
        ResponseDraftingOutput: The structured output containing the drafted response

    """

    parser = PydanticOutputParser(pydantic_object=ResponseDraftingOutput)

    prompt = PromptTemplate(

        template="""
    You are a professional customer support agent for a large e-commerce platform.

    Your task:
    - Draft a safe, policy-compliant response for a human support agent to review.
    - Follow the provided policy strictly.
    - Use previous resolved tickets only as reference, not as guarantees.
    - Do NOT make promises outside the policy.
    - Do NOT mention internal processes or timelines unless stated in the policy.
    - Maintain a professional and calm tone at all times.

    Ticket Id:
    {ticket_id}

    Customer issue:
    {query}

    Relevant policy:
    {policy}

    Previous resolved tickets (for reference only):
    {previous_record}

    --- OUTPUT RULES ---
    {format_instructions}

    If no specific policy applies, set "used_policy" to null.
    """,

        input_variables=["ticket_id", "query", "policy", "previous_record"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt = prompt.format(
        ticket_id=ticket_id,
        query=query,
        policy=policy or "No specific Policy Provided",
        previous_record=previous_record or "No Previous Records Found",
    )

    llm_result = llm.invoke(prompt)
    structured_output = parser.parse(llm_result.content)

    return structured_output


def save_draft_to_db(
            ticket_id: str,
            issue: str,
            reply: str,
            reply_tone: str,
            confidence: float,
            used_policy: str,
            previously_solved_ticket_id: str,
            ticket_creation_time: str,
            metadata: dict
        ) -> None:
    """
    Save a draft ticket to the database.

    Args:
        ticket_id (str): ID of the ticket.
        issue (str): Issue description.
        reply (str): Drafted reply.
        reply_tone (str): Tone of the reply.
        confidence (float): Confidence score of the drafted reply.
        used_policy (str): Policy used for drafting the reply.
        previously_solved_ticket_id (str): ID of the previously solved ticket used as reference.
        ticket_creation_time (str): Creation time of the ticket.
        metadata (dict): Additional metadata.

    Returns:
        None
    """

    draft_tickets_collection.insert_one({
        "ticket_id": ticket_id,
        "issue": issue,
        "reply": reply,
        "reply_tone": reply_tone,
        "confidence": confidence,
        "used_policy": used_policy,
        "previously_solved_ticket_id": previously_solved_ticket_id or None,
        "ticket_creation_time": ticket_creation_time,
        "metadata": metadata,
    })


def perform_ai_drafting(
            ticket: dict
        ) -> None:

    """
    Perform AI drafting for a given ticket and save the draft to the database.

    Args:
        ticket (dict): Dictionary containing ticket details.

    Returns:
        None
    """

    ticket_id = ticket['ticket_id']
    issue = ticket['issue']
    ticket_creation_time = ticket['ticket_creation_time']
    metadata = ticket['metadata']

    # fetching policy and metadata

    retrieved_policy = policy_vector_db.similarity_search_with_score(issue, k=3)
    retrieved_records = previous_record_vector_db.similarity_search_with_score(issue, k=5)

    structured_result = response_drafting(ticket_id, issue, retrieved_policy, retrieved_records)

    reply = structured_result.reply
    reply_tone = structured_result.tone
    used_policy = structured_result.used_policy
    previously_solved_ticket_id = structured_result.used_reference_ticket_id

    confidence = structured_result.confidence

    save_draft_to_db(
        ticket_id,
        issue,
        reply,
        reply_tone,
        confidence,
        used_policy,
        previously_solved_ticket_id,
        ticket_creation_time,
        metadata
    )


if __name__ == "__main__":

    while True:

        new_ticket = pending_tickets_collection.find_one_and_update(
            {"metadata.drafted": False},           # find condition
            {"$set": {"metadata.drafted": True}},  # update
            return_document=pymongo.ReturnDocument.AFTER   # return updated full document
        )

        if not new_ticket:
            time.sleep(5)   # prevents CPU burn
            continue

        try:
            print("Processing Ticket ID:", new_ticket["ticket_id"])
            perform_ai_drafting(new_ticket)
            print(f"Ticket ID: {new_ticket['ticket_id']} is Successfully Drafted")

        except ConnectionFailure as e:
            # rollback if AI crashes
            pending_tickets_collection.update_one(
                {"ticket_id": new_ticket["ticket_id"]},
                {
                    "$set": {"metadata.drafted": False}
                }
            )
            print("Error processing ticket:", e)
