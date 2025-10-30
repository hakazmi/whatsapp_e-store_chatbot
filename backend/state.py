"""
State management for the hierarchical agent system.
Defines the conversation state and message formats.
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Main state for the shopping assistant conversation.
    
    Attributes:
        messages: Conversation history (auto-merged via add_messages)
        user_email: User's email for order tracking
        user_phone: User's phone number
        user_name: User's name
        cart_items: Current items in cart
        current_intent: Detected user intent (search, checkout, track)
        awaiting_confirmation: Whether we're waiting for user confirmation
        last_search_results: Cached product search results
        pending_order_data: Order data pending confirmation
        session_id: Unique session identifier
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_email: str
    user_phone: str
    user_name: str
    cart_items: list[dict]
    current_intent: Literal["search", "checkout", "track", "general", ""]
    awaiting_confirmation: bool
    last_search_results: list[dict]
    pending_order_data: dict
    session_id: str
    last_order_number: str
    last_order_email: str


class SubAgentState(TypedDict):
    """
    State passed to sub-agents for specialized tasks.
    Simpler than main state, focused on specific operations.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    task_input: dict  # Input parameters for the specific task
    task_output: dict  # Output from the sub-agent
    error: str  # Error message if any


def create_initial_state(session_id: str) -> AgentState:
    """Create a fresh state for a new conversation."""
    return {
        "messages": [],
        "user_email": "",
        "user_phone": "",
        "user_name": "",
        "cart_items": [],
        "current_intent": "",
        "awaiting_confirmation": False,
        "last_search_results": [],
        "pending_order_data": {},
        "session_id": session_id
    }