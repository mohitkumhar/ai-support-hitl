"""
AI Support Human in the Loop (HITL) Dashboard
This is the main Streamlit Application file that provides
a user interface for support agents to review, edit,
and manage support tickets with AI assistance.
"""

import os
import streamlit as st
import pymongo

from dotenv import load_dotenv

from app.utils import (
    fetch_similar_past_tickets,
    fetch_similar_policy,
    move_pending_ticket_to_completed_in_db,
    move_drafted_ticket_to_completed_in_db,
    connect_mongo_db,
    move_escalated_ticket_to_completed_in_db,
    call_llm_to_rephase,
    move_tickets_to_escalated_tickets_in_db
)


def main():

    load_dotenv()



    OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")

    client = pymongo.MongoClient(os.getenv("MONGO_URI"))

    db = client["ai_support_system"]

    solved_tickets_collection = db["solved_tickets"]
    pending_tickets_collection = db["pending_tickets"]
    pending_drafted_ticket_collection = db['ai_pending_drafted_tickets']
    escalated_tickets_collection = connect_mongo_db("escalated_tickets")


    # --- PAGE CONFIG ---
    st.set_page_config(page_title="AI Support Co-Pilot", layout="wide")


    # --- MOCK DATA (Replace with your Vector DB/Database logic) ---
    def get_pending_tickets(limit: int = 10) -> list:
        """
        To fetch the Pening Ticket from the DB

        Args:
            limit (int, optional): Number of tickets to fetch. Defaults to 10.

        Returns:
            list: list of pending tickets
        """
        fetch_pending_tickets = list(
            pending_tickets_collection.find({}).sort({"created_at": -1}).limit(limit)
        )
        return fetch_pending_tickets


    def handle_rephase_using_ai_click(current_text: str, temperature: float, purpose: str) -> None:
        """
        Rephase the current text using AI and update the session state.

        Args:
            current_text (str): The text to be rephased.
            temperature (float): The temperature of LLM.
            purpose (str): The purpose of rephasing, e.g., "pending", "drafted", or "escalated".

        Returs:
            None
        """
        rephased_text = call_llm_to_rephase(current_text=current_text, temperature=temperature)

        if purpose == "pending":
            st.session_state.pending_draft = rephased_text
        if purpose == "drafted":
            st.session_state.drafted_draft = rephased_text
        if purpose == "escalated":
            st.session_state.escalated_draft = rephased_text


    def get_drafted_tickets(limit: int = 10) -> list:
        """
        Fetch drafted tickets from the database.

        Args:
            limit (int, optional): Number of tickets to fetch. Defaults to 10.

        Returns:
            list: List of drafted tickets
        """

        pending_drafted_tickets = list(
            pending_drafted_ticket_collection.find({}).sort({"created_at": -1}).limit(limit)
        )
        return pending_drafted_tickets


    def get_escalated_tickets(limit: int = 10) -> list:
        """
        Fetch escalated tickets from the database.

        Args:
            limit (int, optional): Number of tickets to fetch. Defaults to 10.

        Returns:
            list: list of escalated tickets
        """

        fetched_escalated_tickets = list(
            escalated_tickets_collection.find({}).sort({"created_at": -1}).limit(limit)
        )
        return fetched_escalated_tickets


    def get_completed_tickets(limit: int = 10) -> list:
        """
        Fetch completed tickets from the database.

        Args:
            limit (int, optional): Number of Tickets to Fetch. Defaults to 10.

        Returns:
            list: list of completed tickets
        """

        solved_tickets = list(solved_tickets_collection.find({}).sort({"created_at": -1}).limit(limit))
        return solved_tickets


    # --- UI STYLING ---
    st.markdown("""
        <style>
        .confidence-high { color: #28a745; font-weight: bold; }
        .confidence-med { color: #ffc107; font-weight: bold; }
        .confidence-low { color: #dc3545; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)


    # --- SIDEBAR ---
    # --- SIDEBAR ---

    st.sidebar.title("🛠️ Dashboard Control")
    # This selector solves the logic conflict by letting you choose which mode to activate
    # app_mode = st.sidebar.radio("Select View:", ["Pending", "Drafted", "Escalated", "Completed"])
    app_mode = st.sidebar.radio("Select View:", ["Escalated", "Pending", "Drafted", "Completed"])
    st.sidebar.divider()

    # Initialize all variables to None to prevent logic overlap
    current_pending_ticket = None
    current_drafted_ticket = None
    current_escalated_ticket = None
    current_completed_ticket = None

    # --- PENDING SECTION ---
    if app_mode == "Pending":
        st.sidebar.subheader("🎫 Pending Reviews")
        pending_tickets = get_pending_tickets(st.session_state.get("pending_tickets_limit", 10))
        if pending_tickets:
            pending_ticket_id = st.sidebar.selectbox(
                "Select a ticket to review:",
                [t["ticket_id"] for t in pending_tickets],
                key="pending"
            )
            pending_map = {t["ticket_id"]: t for t in pending_tickets}
            current_pending_ticket = pending_map.get(pending_ticket_id)

            if st.sidebar.button("Load more Pending Tickets"):
                st.session_state.pending_tickets_limit = st.session_state.get(
                        "pending_tickets_limit", 10
                    ) + 10
                st.rerun()
            total_tickets_in_db = pending_tickets_collection.count_documents({})
            st.sidebar.caption(f"Showing {len(pending_tickets)} of {total_tickets_in_db} tickets")

        else:
            st.sidebar.info("No pending tickets found.")


    # --- DRAFTED SECTION ---
    elif app_mode == "Drafted":
        st.sidebar.subheader("🎫 Drafted Reviews")
        drafted_tickets = get_drafted_tickets(st.session_state.get("drafted_tickets_limit", 10))
        if drafted_tickets:
            drafted_ticket_id = st.sidebar.selectbox(
                "Select a ticket to review:",
                [t["ticket_id"] for t in drafted_tickets],
                key="drafted"
            )
            drafted_map = {t["ticket_id"]: t for t in drafted_tickets}
            current_drafted_ticket = drafted_map.get(drafted_ticket_id)

            if st.sidebar.button("Load more Drafted Tickets"):
                st.session_state.drafted_tickets_limit = st.session_state.get(
                        "drafted_tickets_limit", 10
                    ) + 10
                st.rerun()

            total_drafted_tickets_in_db = pending_drafted_ticket_collection.count_documents({})
            st.sidebar.caption(
                f"Showing {len(drafted_tickets)} of {total_drafted_tickets_in_db} tickets"
            )

        else:
            st.sidebar.info("No drafted tickets found.")

    # --- ESCALATION SECTION ---
    elif app_mode == "Escalated":
        st.sidebar.subheader("🎫 Escalated Reviews")
        escalated_tickets = get_escalated_tickets(st.session_state.get("escalated_tickets_limit", 10))
        if escalated_tickets:
            escalated_ticket_id = st.sidebar.selectbox(
                "Select a ticket to review:",
                [t["ticket_id"] for t in escalated_tickets],
                key="drafted"
            )
            escalated_map = {t["ticket_id"]: t for t in escalated_tickets}
            current_escalated_ticket = escalated_map.get(escalated_ticket_id)

            if st.sidebar.button("Load more Escalated Tickets"):
                st.session_state.escalated_tickets_limit = st.session_state.get(
                        "escalated_tickets_limit", 10
                    ) + 10
                st.rerun()

            total_escalated_tickets_in_db = escalated_tickets_collection.count_documents({})
            st.sidebar.caption(
                f"Showing {len(escalated_tickets)} of {total_escalated_tickets_in_db} tickets"
            )

        else:
            st.sidebar.info("No Escalated tickets found.")

    # --- COMPLETED SECTION ---
    elif app_mode == "Completed":
        st.sidebar.subheader("🎫 Completed Tickets")
        completed_tickets = get_completed_tickets(st.session_state.get("completed_tickets_limit", 10))
        if completed_tickets:
            completed_ticket_id = st.sidebar.selectbox(
                "Select a past completed ticket:",
                [t["ticket_id"] for t in completed_tickets],
                key="completed"
            )
            completed_map = {t["ticket_id"]: t for t in completed_tickets}
            current_completed_ticket = completed_map.get(completed_ticket_id)

            if st.sidebar.button("Load more Escalated Tickets"):
                st.session_state.completed_tickets_limit = st.session_state.get(
                        "completed_tickets_limit", 10
                    ) + 10
                st.rerun()

            total_completed_tickets_in_db = solved_tickets_collection.count_documents({})
            st.sidebar.caption(
                f"Showing {len(completed_tickets)} of {total_completed_tickets_in_db} tickets"
            )

        else:
            st.sidebar.info("No completed tickets found.")


    # --- MAIN INTERFACE ---
    st.title("🚀 AI Support Agent Dashboard")
    st.divider()

    # Priority: Pending ticket view
    if current_pending_ticket:
        MODE = "pending"
        current_ticket = current_pending_ticket

    elif current_drafted_ticket:
        MODE = "drafted"
        current_ticket = current_drafted_ticket

    elif current_escalated_ticket:
        MODE = "escalated"
        current_ticket = current_escalated_ticket

    elif current_completed_ticket:
        MODE = "completed"
        current_ticket = current_completed_ticket

    else:
        st.info("Please select a ticket from the sidebar.")
        st.stop()


    def move_tickets_to_completed_tickets_in_db(
                ticket_id: str,
                resp: str,
                purpose: str
            ) -> None:
        """
        Move Tickets to Completed Tickets in database.

        Args:
            ticket_id (str): The Ticket ID to be moved.
            resp (str): The response to be saved.
            purpose (str): The purpose of moving, e.g., "pending", "drafted", or "escalated".

        Returns:
            None
        """

        # Perform database logic
        if purpose == "pending":
            move_pending_ticket_to_completed_in_db(ticket_id=ticket_id, response=resp)
        if purpose == "drafted":
            move_drafted_ticket_to_completed_in_db(ticket_id=ticket_id, response=resp)
        if purpose == "escalated":
            move_escalated_ticket_to_completed_in_db(ticket_id=ticket_id, response=resp)

        # Save the success message in session state
        st.session_state["success_msg"] = f"Ticket {ticket_id} approved and moved to completed!"


    if MODE == "pending":
        col1, col2 = st.columns([1.5, 1])
        if "success_msg" in st.session_state:
            st.toast(st.session_state["success_msg"], icon="✅")
            # Clear it so it doesn't pop up again on the next interaction
            del st.session_state["success_msg"]

        with col1:
            st.subheader("📩 Customer Inquiry")
            st.info(f"**Query:** {current_ticket.get('issue', 'N/A')}")

            # ---- AI RESPONSE DRAFT (NOT AVAILABLE YET) ----
            st.subheader("✏️ Response Draft")

            AI_DRAFT = "This Ticket is not Yet Drafted, Please Write Response Manually..."

            if 'pending_draft' not in st.session_state:
                st.session_state.pending_draft = AI_DRAFT

            final_response = st.text_area(
                "Draft response:",
                value=st.session_state.pending_draft,
                height=250
            )

            # print(f"{final_response}")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.button(
                    "✅ Approve & Send",
                    key=f"approve_{current_ticket['ticket_id']}",
                    on_click=move_tickets_to_completed_tickets_in_db,
                    args=(current_ticket['ticket_id'], final_response, 'pending')
                )

            with c2:
                st.button(
                    "🔄 RePhase Using AI",
                    key=f"rephrase_{current_ticket['ticket_id']}",
                    on_click=handle_rephase_using_ai_click,
                    # Access the slider value via session_state
                    args=(final_response, st.session_state.get("rephrase_temp_value", 0.5), "pending")
                )

                # st.toast("Regenerating response...")

            with c3:
                st.button(
                    "🚩 Escalate",
                    key=f"escalate_{current_ticket['ticket_id']}",
                    on_click=move_tickets_to_escalated_tickets_in_db,
                    args=(current_ticket['ticket_id'], 'pending_tickets')
                )

        # -------- RIGHT PANEL --------
        with col2:
            st.subheader("📚 Ticket Context")

            with st.expander("📌 Metadata", expanded=True):
                st.write(f"**Category:** {current_ticket['metadata']['category']}")
                st.write(f"**Priority:** {current_ticket['metadata']['priority']}")
                st.write(f"**Drafted:** {current_ticket['metadata']['is_drafted']}")

            with st.expander("🕒 Created At"):
                st.write(current_ticket.get("ticket_creation_time", "N/A"))

            with st.expander("🔁 Similar Past Tickets"):
                fetched_similar_past_tickets = fetch_similar_past_tickets(
                    current_ticket['issue'],
                    open_ai_key=OPEN_AI_KEY
                )

                # print("#########: ", fetched_similar_past_tickets)

                if fetched_similar_past_tickets:
                    for i, past_tickets in enumerate(fetched_similar_past_tickets, 1):
                        st.markdown(f"**{i}**. Confidence: `{past_tickets[1]}`")

                        with st.expander("View Past Tickets"):
                            st.write(f"**Issue**: {past_tickets[0].page_content}")
                            st.write(f"**Resolution**:  {past_tickets[0].metadata['resolution']}")

            with st.expander("🔁 Related Policy"):
                fetched_similar_policy = fetch_similar_policy(
                    issue=current_ticket['issue'],
                    open_ai_key=OPEN_AI_KEY
                )

                # print(fetched_similar_policy)
                if fetched_similar_policy:
                    for i, policy in enumerate(fetched_similar_policy, 1):
                        st.markdown(f"**{i}**. Confidence: `{1 / (1 + (policy[1]))}`")
                        with st.expander("View Policy"):
                            st.write(policy[0].page_content)

            st.slider(
                "Adjust Rephrase Temperature:",
                0.0, 1.0, 0.5, 0.01,
                key="rephrase_temp_value"  # This creates st.session_state.rephrase_temp_value
            )


    elif MODE == "drafted":
        col1, col2 = st.columns([1.5, 1])

        if "success_msg" in st.session_state:
            st.toast(st.session_state["success_msg"], icon="✅")
            # Clear it so it doesn't pop up again on the next interaction
            del st.session_state["success_msg"]

        with col1:
            st.subheader("📩 Customer Inquiry [DRAFTED RESPONSE]")
            # print(current_ticket)
            st.info(f"**Query:** {current_ticket['issue']}")

            score = current_ticket['confidence']

            st.subheader("🤖 AI Confidence")
            if score > 0.9:
                st.success(f"{score} - High confidence")
            elif score > 0.7:
                st.warning(f"{score} - Medium confidence")
            else:
                st.error(f"{score} - Low confidence (Manual review recommended)")

            st.subheader("✏️ Response Draft")
            # ai_draft_response = current_ticket['ai_drafted_response']
            ai_draft = current_ticket.get(
                "ai_drafted_response",
                "AI unable to Draft it, Write Your own..."
            )

            if 'drafted_draft' not in st.session_state:
                st.session_state.drafted_draft = ai_draft

            final_response = st.text_area(
                "Edit AI draft before sending:",
                value=st.session_state.drafted_draft,
                height=250
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.button(
                    "✅ Approve & Send",
                    key=f"approve_{current_ticket['ticket_id']}",
                    on_click=move_tickets_to_completed_tickets_in_db,
                    args=(current_ticket['ticket_id'], final_response, "drafted")
                )

            with c2:
                st.button(
                    "🔄 RePhase Using AI",
                    key=f"rephrase_{current_ticket['ticket_id']}",
                    on_click=handle_rephase_using_ai_click,
                    # Access the slider value via session_state
                    args=(final_response, st.session_state.get("rephrase_temp_value", 0.5), "drafted")
                )

            with c3:
                st.button(
                    "🚩 Escalate",
                    key=f"escalate_{current_ticket['ticket_id']}",
                    on_click=move_tickets_to_escalated_tickets_in_db,
                    args=(current_ticket['ticket_id'], 'ai_pending_drafted_tickets')
                )

        with col2:
            st.subheader("📚 AI Context")
            with st.expander("📌 Metadata", expanded=True):
                st.write(f"**Ticket Used as Reference:** {current_ticket['used_reference_ticket_id']}")

            with st.expander("🔁 Similar Past Tickets"):

                fetched_similar_past_tickets = fetch_similar_past_tickets(
                    issue=current_ticket['issue'],
                    open_ai_key=OPEN_AI_KEY
                )
                # print("%%%", fetched_similar_past_tickets)

                if fetched_similar_past_tickets:
                    for i, tickets in enumerate(fetched_similar_past_tickets, 1):
                        st.markdown(f"**{i}**. Confidence: {1 / (1 + tickets[1])}")

                        with st.expander("Reference Tickets"):
                            st.write(f"**Issue**: {tickets[0].page_content}")
                            st.write(f"**Resolution**: {tickets[0].metadata['resolution']}")

            with st.expander("📄 Matched Policy", expanded=True):
                fetched_similar_policy = fetch_similar_policy(
                        issue=current_ticket['issue'],
                        open_ai_key=OPEN_AI_KEY
                    )

                # print("$$$$$$$",fetched_similar_policy)
                if fetched_similar_policy:
                    for i, policy in enumerate(fetched_similar_policy, 1):
                        st.markdown(f"**{i}**. Confidence: {1 / (1 + policy[1])}")

                        with st.expander("View Policy"):
                            st.write(policy[0].page_content)

            st.slider(
                "Adjust Rephrase Temperature:",
                0.0, 1.0, 0.5, 0.01,
                key="rephrase_temp_value"  # This creates st.session_state.rephrase_temp_value
            )


    elif MODE == "escalated":
        col1, col2 = st.columns([1.5, 1])

        if "success_msg" in st.session_state:
            st.toast(st.session_state["success_msg"], icon="✅")
            # Clear it so it doesn't pop up again on the next interaction
            del st.session_state["success_msg"]

        with col1:
            st.subheader("📩 Customer Inquiry [ESCALATED MESSAGES]")
            # print(current_ticket)
            st.info(f"**Query:** {current_ticket['issue']}")

            st.subheader("✏️ Response Draft")
            ai_draft = current_ticket.get(
                "ai_drafted_response",
                "This Ticket is Escalated, Kindly Review it..."
            )

            if "escalated_draft" not in st.session_state:
                st.session_state.escalated_draft = ai_draft

            final_response = st.text_area(
                "This is Escalated Ticket, Kindly Review it...",
                value=st.session_state.escalated_draft,
                height=250
            )

            c1, c2 = st.columns(2)
            with c1:
                st.button(
                    "✅ Approve & Send",
                    key=f"approve_{current_ticket['ticket_id']}",
                    on_click=move_tickets_to_completed_tickets_in_db,
                    args=(current_ticket['ticket_id'], final_response, "escalated")
                )

            with c2:
                st.button(
                    "🔄 RePhase Using AI",
                    key=f"rephrase_{current_ticket['ticket_id']}",
                    on_click=handle_rephase_using_ai_click,
                    # Access the slider value via session_state
                    args=(final_response, st.session_state.get("rephrase_temp_value", 0.5), "escalated")
                )

        with col2:
            st.subheader("📚 AI Context")
            with st.expander("📌 Metadata", expanded=True):

                st.write(
                    f"**Ticket Creation Time:** {current_ticket['metadata']['ticket_creation_time']}"
                )

                if "used_reference_ticket_id" in current_ticket:
                    st.write(
                        f"**Ticket Used as Reference:** {current_ticket['used_reference_ticket_id']}"
                    )
                st.write(f"**Ticket Category:** {current_ticket['metadata']['category']}")

            with st.expander("🔁 Similar Past Tickets"):

                fetched_similar_past_tickets = fetch_similar_past_tickets(
                    issue=current_ticket['issue'],
                    open_ai_key=OPEN_AI_KEY
                )
                # print("%%%", fetched_similar_past_tickets)

                if fetched_similar_past_tickets:
                    for i, tickets in enumerate(fetched_similar_past_tickets, 1):
                        st.markdown(f"**{i}**. Confidence: {1 / (1 + tickets[1])}")

                        with st.expander("Reference Tickets"):
                            st.write(f"**Issue**: {tickets[0].page_content}")
                            st.write(f"**Resolution**: {tickets[0].metadata['resolution']}")

            with st.expander("📄 Matched Policy", expanded=True):
                fetched_similar_policy = fetch_similar_policy(
                    issue=current_ticket['issue'], open_ai_key=OPEN_AI_KEY
                )

                # print("$$$$$$$",fetched_similar_policy)
                if fetched_similar_policy:
                    for i, policy in enumerate(fetched_similar_policy, 1):
                        st.markdown(f"**{i}**. Confidence: {1 / (1 + policy[1])}")

                        with st.expander("View Policy"):
                            st.write(policy[0].page_content)

            st.slider(
                "Adjust Rephrase Temperature:",
                0.0, 1.0, 0.5, 0.01,
                key="rephrase_temp_value"  # This creates st.session_state.rephrase_temp_value
            )


    elif MODE == "completed":
        st.subheader("✅ Completed Ticket Summary")

        col1, col2 = st.columns(2)
        # print(f"This is compelted section: {current_ticket}")

        with col1:
            st.markdown(f"**Ticket ID:** {current_ticket['ticket_id']}")
            st.markdown(f"**Customer Query:** {current_ticket['issue']}")
            st.markdown(f"**Resolution:** {current_ticket['resolution']}")

        with col2:
            st.markdown(f"**Confidence Score:** {current_ticket['confidence']}")
            st.markdown(f"**Raised On:** {current_ticket['metadata']['ticket_creation_time']}")
            st.markdown(f"**Resolved On:** {current_ticket['metadata']['ticket_closure_time']}")
            st.markdown("**Status:** Closed ✅")

        with st.expander("📜 Full AI Drafting Response"):
            st.write(current_ticket.get("ai_drafted_response", "N/A"))

        st.info("Completed tickets are only for read-only purposes.")


    # --- FOOTER: SYSTEM FEEDBACK ---
    st.divider()
    st.caption("AI Support System v1.2 | Built with RAG & Human-in-the-Loop")

if __name__ == "__main__":
    main()