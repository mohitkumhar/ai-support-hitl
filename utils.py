"""
    Utilities File for AI Support System
    This file contains utility functions to connect to MongoDB,
    vector databases, and interact with OpenAI models.
"""

import os
import datetime
from typing import List
from dotenv import load_dotenv

import pymongo
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

OPEN_AI_KEY = os.getenv("OPEN_AI_KEY")


def connect_mongo_db(
            collection_name: str,
            database_name: str = 'ai_support_system'
        ) -> Collection:

    """Function to connect with MongoDB and return the collection object.

    Args:
        collection_name (str): name of the collection to connect
        database_name (str, optional): name of the db to connect. Defaults to 'ai_support_system'.

    Returns:
        _type_: Collection: MongoDB Collection Object
    """
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]

    return collection


# creating LLM Model Object
def get_llm_object(
            open_ai_key: str,
            model_name: str = 'openai/gpt-4o-mini',
            base_url: str = "https://openrouter.ai/api/v1",
            temperature: float = 0.2,
            verbose: bool = True
        ) -> ChatOpenAI:
    """Function to create the LLM object

    Args:
        open_ai_key (str): OpenAI api key for authentication
        model_name (str, optional): Name of the Model to use. Defaults to 'openai/gpt-4o-mini'.
        base_url (str, optional): Base URL for model. Defaults to "https://openrouter.ai/api/v1".
        temperature (float, optional): temperature for the model. Defaults to 0.2.
        verbose (bool, optional): Whether to enable verbose logging. Defaults to True.

    Returns:
        _type_: ChatOpenAI: LLM Model Object
    """
    llm = ChatOpenAI(
            model_name=model_name,
            api_key=open_ai_key,
            base_url=base_url,
            temperature=temperature,
            verbose=verbose,
        )

    return llm


# creating embedding model object
def get_embedding_model(
            open_ai_key: str
        ) -> OpenAIEmbeddings:
    """Function to create OpenAI Embeddings Object

    Args:
        open_ai_key (str): Open AI API key

    Returns:
        OpenAIEmbeddings: OpenAIEmbeddings: Embedding Model Object
    """
    embeddings = OpenAIEmbeddings(
        api_key=open_ai_key,
        model="text-embedding-3-large",
        base_url="https://openrouter.ai/api/v1",
    )

    return embeddings


# connecting to vector DB Chroma

def connect_policy_vectordb(
            open_ai_key: str
        ) -> Chroma:
    """Function to connect to vectorDB

    Args:
        open_ai_key (str): Open AI API key

    Returns:
        _type_: Chroma: VectorDB Object
    """
    policy_vector_db = Chroma(
        embedding_function=get_embedding_model(open_ai_key=open_ai_key),
        collection_name="Policy",
        persist_directory="Company_Info_VectorDB"
    )

    return policy_vector_db


def connect_previous_record_vector_db(
            open_ai_key: str
        ) -> Chroma:
    """Function to connect to Previous Records VectorDB

    Args:
        open_ai_key (str): Open AI API key

    Returns:
        _type_: Chroma: VectorDB Object
    """

    previous_record_vector_db = Chroma(
        collection_name="PreviousData",
        embedding_function=get_embedding_model(open_ai_key=open_ai_key),
        persist_directory="Company_Info_VectorDB"
    )

    return previous_record_vector_db


def fetch_confidence_score(
            issue: str
        ) -> float:
    """Fetch Confidence Score from the given issue

    Args:
        issue (str): Customer Issue

    Returns:
        _type_: float: Confidence Score
    """
    previous_record_vector_db = connect_previous_record_vector_db(open_ai_key=OPEN_AI_KEY)
    previous_record_retriever = previous_record_vector_db.similarity_search_with_score(issue, k=3)

    store = {}

    for doc, distance in previous_record_retriever:
        store[doc.page_content] = (doc.metadata['ticket_id'], 1 / (1 + distance))

    return store


def connect_vector_db(
            collection_name: str,
            open_ai_key: str
        ) -> Chroma:
    """Function to Connect VectorDB

    Args:
        collection_name (str): Name of the collection
        open_ai_key (str): Open AI API key

    Returns:
        _type_: Chroma: VectorDB Object
    """
    embeddings = OpenAIEmbeddings(
        open_ai_key=open_ai_key,
        model="text-embedding-3-large",
        base_url="https://openrouter.ai/api/v1",
    )

    vector_db = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="Company_Info_VectorDB",
    )

    return vector_db


def fetch_similar_past_tickets(
            issue: str,
            open_ai_key: str
        ) -> List[str]:
    """Function to fetch similar past tickets from VectorDB

    Args:
        issue (str): Customer issue
        open_ai_key (str): OpenAI API key

    Returns:
        _type_: List[str]: List of similar past tickets
    """
    vector_db = connect_vector_db(collection_name="PreviousData", open_ai_key=open_ai_key)

    similar_records = vector_db.similarity_search_with_score(query=issue, k=3)

    return similar_records


def fetch_similar_policy(
            issue: str,
            open_ai_key: str
        ) -> List[str]:
    """Fetch Similar Policy based on User Query

    Args:
        issue (str): Customer Issue
        open_ai_key (str): Open AI API Key

    Returns:
        _type_: List[str]: List of Similar Policies
    """
    vector_db = connect_vector_db(collection_name="Policy", open_ai_key=open_ai_key)

    similar_docs = vector_db.similarity_search_with_score(query=issue, k=3)

    return similar_docs


def fetch_ai_drafted_document(
            ticket_id: str
        ) -> pymongo.cursor.Cursor:
    """ Fetch AI Drafted Document from MongoDB

    Args:
        ticket_id (str): Ticket ID

    Returns:
        _type_: pymongo.cursor.Cursor: Cursor Object containing the drafted document
    """

    ai_drafted_tickets_collection = connect_mongo_db("ai_pending_drafted_tickets")
    return ai_drafted_tickets_collection.find({'ticket_id': ticket_id})


def fetch_ticket_response_and_confidence(
            ticket_id: str
        ) -> tuple:
    """ Get Ticket Response and Confidence from MongoDB

    Args:
        ticket_id (str): Ticket ID

    Returns:
        _type_: tuple: Tuple containing the drafted response and confidence score
    """
    ai_drafted_response = ''
    ai_drafted_response_confidence = 0

    for values in fetch_ai_drafted_document(ticket_id):
        ai_drafted_response = values['reply']
        ai_drafted_response_confidence = values['confidence']

        return ai_drafted_response, ai_drafted_response_confidence


def remove_drafted_ticket_from_db(
            ticket_id: str
        ) -> bool:
    """Remove Drafted Ticket from MongoDB

    Args:
        ticket_id (str): Ticket ID

    Returns:
        _type_: bool: True if the ticket is removed successfully
    """
    try:
        drafted_pending_tickets_collection = connect_mongo_db("ai_pending_drafted_tickets")
        drafted_pending_tickets_collection.delete_one({'ticket_id': ticket_id})
        return True

    except PyMongoError as e:
        print(f"Error removing drafted ticket: {e}")
        return False


def move_escalated_ticket_to_completed_in_db(
            ticket_id: str,
            response: str
        ) -> bool:
    """Move Escalated Ticket to Completed Ticket Collection in DataBase

    Args:
        ticket_id (str): Ticket ID
        response (str): Resolution Response

    Returns:
        _type_: bool: True if the ticket is moved successfully
    """

    try:
        escalated_tickets_collection = connect_mongo_db(collection_name="escalated_tickets")
        completed_tickets_collection = connect_mongo_db(collection_name="solved_tickets")

        ticket_to_move = escalated_tickets_collection.find_one_and_delete({"ticket_id": ticket_id})
        ticket_to_move.pop('_id', None)

        completed_tickets_collection.insert_one({

            'ticket_id': ticket_id,
            'issue': ticket_to_move['issue'],
            "resolution": response,
            "ai_drafted_response":
                ticket_to_move.get('ai_drafted_response', "Senior agent handled the response"),
            "used_policy": ticket_to_move.get('used_policy', None),
            "used_reference_ticket_id": ticket_to_move.get('used_reference_ticket_id', None),
            'confidence': ticket_to_move.get('confidence', "Senior agent handled the response"),
            'metadata':
                {
                    'ticket_creation_time': ticket_to_move['metadata']['ticket_creation_time'],
                    'ticket_closure_time': datetime.datetime.now(),
                    'category': ticket_to_move['metadata']['category'],
                    'priority': ticket_to_move['metadata']['priority'],
                    'is_drafted': ticket_to_move['metadata']['is_drafted'],
                    'tone': None,
                }
        })

        return True

    except PyMongoError as e:
        print(f"Error moving escalated ticket to completed: {e}")
        return False


def move_pending_ticket_to_completed_in_db(
            ticket_id: str,
            response: str
        ) -> bool:
    """
    Move Pending Tickets to Complete Tickets Collection in MongoDB:

    Args:
        ticket_id (str): Ticket ID
        response (str): Resolution Response
    Returns:
        _type_: bool: True if the ticket is moved successfully, False otherwise
    """

    try:
        pending_tickets_collection = connect_mongo_db("pending_tickets")
        completed_tickets_collection = connect_mongo_db("solved_tickets")

        ticket_to_move = pending_tickets_collection.find_one_and_delete({"ticket_id": ticket_id})
        ticket_to_move.pop('_id', None)

        if ticket_to_move['metadata']['is_drafted'] is False:
            confidence = None
            ai_drafted_response = None
            tone = None
        else:
            ai_drafted_response, confidence = fetch_ticket_response_and_confidence(
                ticket_to_move['ticket_id']
            )
            tone = ticket_to_move['tone']

        if ticket_to_move['metadata']['is_drafted'] is False:
            remove_drafted_ticket_from_db(ticket_id=ticket_id)

        completed_tickets_collection.insert_one({

            'ticket_id': ticket_id,
            'issue': ticket_to_move['issue'],
            "resolution": response,
            "ai_drafted_response": ai_drafted_response,
            'confidence': confidence,
            'metadata':
                {
                    'ticket_creation_time': ticket_to_move['metadata']['ticket_creation_time'],
                    'ticket_closure_time': datetime.datetime.now(),
                    'category': ticket_to_move['metadata']['category'],
                    'priority': ticket_to_move['metadata']['priority'],
                    'is_drafted': ticket_to_move['metadata']['is_drafted'],
                    'tone': tone,
                }
        })

        return True

    except PyMongoError as e:
        print(f"Error moving pending ticket to completed: {e}")
        return False


def move_drafted_ticket_to_completed_in_db(
            ticket_id: str,
            response: str
        ) -> bool:
    """Move Drafted Ticket from to Completed Tickets in Database

    Args:
        ticket_id (str): Ticket ID
        response (str): Resolution Response

    Returns:
        _type_: bool: True if the ticket is moved successfully, False otherwise
    """

    try:
        drafted_ticket_collection = connect_mongo_db(collection_name="ai_pending_drafted_tickets")
        completed_tickets_collection = connect_mongo_db(collection_name="solved_tickets")

        ticket_to_move = drafted_ticket_collection.find_one_and_delete({"ticket_id": ticket_id})
        print(ticket_to_move)
        ticket_to_move.pop('_id', None)

        completed_tickets_collection.insert_one({

            'ticket_id': ticket_id,
            'issue': ticket_to_move['issue'],
            "resolution": response,
            "ai_drafted_response": ticket_to_move['ai_drafted_response'],
            "used_policy": ticket_to_move['used_policy'],
            "used_reference_ticket_id": ticket_to_move['used_reference_ticket_id'],
            'confidence': ticket_to_move['confidence'],
            'metadata':
                {
                    'ticket_creation_time': ticket_to_move['metadata']['ticket_creation_time'],
                    'ticket_closure_time': datetime.datetime.now(),
                    'category': ticket_to_move['metadata']['category'],
                    'priority': ticket_to_move['metadata']['priority'],
                    'is_drafted': ticket_to_move['metadata']['is_drafted'],
                    'tone': ticket_to_move['metadata']['tone'],
                }
        })

        return True

    except PyMongoError as e:
        print(f"Error moving drafted ticket to completed: {e}")
        return False


def call_llm_to_rephase(
            current_text: str,
            temperature: float
        ) -> str:
    """
    Rephase the given text to make it more polite and professional.

    Args:
        current_text (str): Current Text
        temperature (float): Temperature for LLM

    Returns:
        _type_: str: Rephased Text
    """

    prompt_template = PromptTemplate(
        template="""
        Your task is to rephase the given text to make it more polite and professional.
        Please ensure that the meaning of the text remains unchanged.
        Text: {current_text}
        """,
        input_variables=['current_text'],
    )

    llm = get_llm_object(
        open_ai_key=OPEN_AI_KEY,
        model_name='openai/gpt-4o-mini',
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        verbose=True
    )

    parser = StrOutputParser()

    final_chain = prompt_template | llm | parser

    print("This is utils, func: ", temperature, current_text)

    return final_chain.invoke(current_text)


def move_tickets_to_escalated_tickets_in_db(
            ticket_id: str,
            from_collection_name: str
        ) -> bool:
    """
    Move Tickets to Escalated Tickets Collection in Database

    Args:
        ticket_id (str): Ticket ID
        from_collection_name (str): Name of the collection from which the ticket is to be moved

    Returns:
        _type_: bool: True if the ticket is moved successfully, False otherwise
    """

    try:

        from_collection = connect_mongo_db(collection_name=from_collection_name)
        escalated_collection = connect_mongo_db(collection_name="escalated_tickets")

        ticket_to_move = from_collection.find_one_and_delete({"ticket_id": ticket_id})
        print("Ticket to move:", ticket_to_move, from_collection_name, ticket_id)
        ticket_to_move.pop('_id', None)

        escalated_collection.insert_one(ticket_to_move)
        return True

    except PyMongoError as e:
        print(f"Error moving ticket to escalated: {e}")
        return False
