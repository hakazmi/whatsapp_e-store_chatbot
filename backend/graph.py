"""
SIMPLIFIED SUPERVISOR GRAPH - WITH ORDER MEMORY
============================
Much simpler graph - just Supervisor node + END
No complex routing logic needed!
Flow:
  User Input → Supervisor (with sub-agent tools) → Response
 
The supervisor decides which sub-agents to call using its LLM intelligence.
CRITICAL: Now persists order info for smart tracking!
"""
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from state import AgentState
from agents import invoke_supervisor, shared_state
import sys
import os
import requests

if os.getenv("LANGCHAIN_TRACING_V2"):
    print("🔍 LangSmith tracing enabled", file=sys.stderr)

# Main API URL for cart sync
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://localhost:8000/api")

def sync_cart_to_backend(session_id: str, cart_items: list):
    """Sync cart to main backend API"""
    try:
        # Clear existing cart
        requests.delete(f"{MAIN_API_URL}/cart/{session_id}", timeout=2)
       
        # Add each item
        for item in cart_items:
            requests.post(
                f"{MAIN_API_URL}/cart/{session_id}/add",
                json={
                    "product_id": item.get("product_id"),
                    "quantity": item.get("quantity", 1),
                    "pricebook_entry_id": item.get("pricebook_entry_id"),
                    "price": item.get("price", 0),
                    "name": item.get("name", ""),
                    "color": item.get("color", ""),
                    "size": item.get("size", ""),
                    "image_url": item.get("image_url", "")
                },
                timeout=2
            )
       
        print(f"✅ Cart synced to backend: {len(cart_items)} items", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Cart sync failed: {e}", file=sys.stderr)

def clear_backend_cart(session_id: str):
    """Clear cart in backend after checkout"""
    try:
        response = requests.delete(f"{MAIN_API_URL}/cart/{session_id}", timeout=2)
        if response.ok:
            print(f"🧹 Backend cart cleared for {session_id}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Failed to clear backend cart: {e}", file=sys.stderr)

# ============================================================================
# SINGLE SUPERVISOR NODE
# ============================================================================

def supervisor_node(state: AgentState) -> AgentState:
    """
    Main supervisor node - handles ALL user requests
    Uses sub-agents as tools for specialized tasks
    """
   
    print("\n🤖 Supervisor Node Processing...", file=sys.stderr)
   
    # Get last user message
    last_message = state["messages"][-1]
    user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
   
    session_id = state.get("session_id", "default")
    print(f" Session: {session_id}", file=sys.stderr)
    print(f" Cart Items: {len(state.get('cart_items', []))}", file=sys.stderr)
    print(f" Last Order: #{state.get('last_order_number', 'None')}", file=sys.stderr)
   
    # Invoke supervisor with current state
    try:
        response = invoke_supervisor(user_message, session_id, state)
       
        # Add supervisor response to messages
        state["messages"].append(AIMessage(content=response))
       
        # Sync state from shared state (updated by sub-agents)
        state["cart_items"] = shared_state.cart_items
        state["last_search_results"] = shared_state.last_search_results
        state["user_name"] = shared_state.user_name
        state["user_email"] = shared_state.user_email
        state["user_phone"] = shared_state.user_phone
        
        # CRITICAL: Persist order memory
        state["last_order_number"] = shared_state.last_order_number
        state["last_order_email"] = shared_state.last_order_email
        
        print(f"💾 Order memory updated: #{shared_state.last_order_number}", file=sys.stderr)

        # Sync cart to backend
        sync_cart_to_backend(session_id, state["cart_items"])

        # Clear backend if order was confirmed
        if "Order Confirmed" in response or "Order Number" in response:
            clear_backend_cart(session_id)
       
        print(f"✅ Supervisor node completed", file=sys.stderr)
       
    except Exception as e:
        print(f"❌ Supervisor node error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        state["messages"].append(AIMessage(content="Sorry, I encountered an error. Please try again."))
   
    return state

# ============================================================================
# BUILD AND COMPILE GRAPH
# ============================================================================

def create_shopping_graph():
    """ 
    Create supervisor multi-agent graph. 
    Supervisor delegates to specialist sub-agents.
    """
    memory = MemorySaver()
    workflow = StateGraph(AgentState)
    
    # Single supervisor node
    workflow.add_node("supervisor", supervisor_node)
    
    # Simple flow: START → supervisor → END
    workflow.add_edge(START, "supervisor")
    workflow.add_edge("supervisor", END)
    
    return workflow.compile(checkpointer=memory)

# Create graph
shopping_assistant_graph = create_shopping_graph()

print("✅ Shopping Assistant Graph Created", file=sys.stderr)
print("🎯 Single Supervisor Node with 4 Sub-Agent Tools:", file=sys.stderr)
print("   🔍 search_products", file=sys.stderr)
print("   🛒 manage_cart", file=sys.stderr)
print("   💳 checkout_order", file=sys.stderr)
print("   📦 track_order (SMART: remembers last order)", file=sys.stderr)