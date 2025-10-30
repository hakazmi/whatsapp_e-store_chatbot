"""
MongoDB configuration and models for chat history
"""
from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "whatsapp_shopping")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# Collections
conversations_collection = db["conversations"]
messages_collection = db["messages"]
sessions_collection = db["sessions"]


def create_indexes():
    """Create indexes for better query performance"""
    # Conversations indexed by phone
    conversations_collection.create_index("phone_number", unique=True)
    
    # Messages indexed by conversation_id and timestamp
    messages_collection.create_index([("conversation_id", 1), ("timestamp", -1)])
    
    # Sessions indexed by phone and session_id
    sessions_collection.create_index("phone_number")
    sessions_collection.create_index("session_id", unique=True)
    
    print("✅ MongoDB indexes created")


def get_or_create_conversation(phone_number: str) -> str:
    """
    Get or create conversation for a phone number
    Returns conversation_id
    """
    conversation = conversations_collection.find_one({"phone_number": phone_number})
    
    if conversation:
        return str(conversation["_id"])
    
    # Create new conversation
    new_conversation = {
        "phone_number": phone_number,
        "created_at": datetime.now(),
        "last_message_at": datetime.now(),
        "message_count": 0
    }
    
    result = conversations_collection.insert_one(new_conversation)
    return str(result.inserted_id)


def save_message(
    conversation_id: str,
    phone_number: str,
    message: str,
    sender: str = "user",  # "user" or "assistant"
    metadata: Optional[Dict] = None
) -> str:
    """
    Save a message to the database
    Returns message_id
    """
    message_doc = {
        "conversation_id": conversation_id,
        "phone_number": phone_number,
        "message": message,
        "sender": sender,
        "timestamp": datetime.now(),
        "metadata": metadata or {}
    }
    
    result = messages_collection.insert_one(message_doc)
    
    # Update conversation stats
    conversations_collection.update_one(
        {"_id": conversation_id},
        {
            "$set": {"last_message_at": datetime.now()},
            "$inc": {"message_count": 1}
        }
    )
    
    return str(result.inserted_id)


def get_conversation_history(
    phone_number: str,
    limit: int = 50
) -> List[Dict]:
    """
    Get conversation history for a phone number
    Returns list of messages sorted by timestamp (newest first)
    """
    conversation = conversations_collection.find_one({"phone_number": phone_number})
    
    if not conversation:
        return []
    
    conversation_id = str(conversation["_id"])
    
    messages = messages_collection.find(
        {"conversation_id": conversation_id}
    ).sort("timestamp", -1).limit(limit)
    
    return [
        {
            "message_id": str(msg["_id"]),
            "message": msg["message"],
            "sender": msg["sender"],
            "timestamp": msg["timestamp"],
            "metadata": msg.get("metadata", {})
        }
        for msg in messages
    ]


def link_session_to_phone(phone_number: str, session_id: str) -> bool:
    """
    Link a session ID to a phone number
    """
    try:
        sessions_collection.update_one(
            {"phone_number": phone_number},
            {
                "$set": {
                    "session_id": session_id,
                    "updated_at": datetime.now()
                },
                "$setOnInsert": {
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"❌ Failed to link session: {e}")
        return False


def get_session_by_phone(phone_number: str) -> Optional[str]:
    """
    Get session ID for a phone number
    """
    session = sessions_collection.find_one({"phone_number": phone_number})
    return session["session_id"] if session else None


def get_phone_by_session(session_id: str) -> Optional[str]:
    """
    Get phone number for a session ID
    """
    session = sessions_collection.find_one({"session_id": session_id})
    return session["phone_number"] if session else None


# Initialize indexes on import
create_indexes()

print("✅ MongoDB connection established")
print(f"📊 Database: {MONGODB_DB}")
print(f"📁 Collections: conversations, messages, sessions")