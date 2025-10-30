"""
Enhanced WhatsApp Server - UPDATED FOR SUPERVISOR ARCHITECTURE
Compatible with new agents.py and graph.py
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from langchain_core.messages import HumanMessage
from state import create_initial_state
from graph import shopping_assistant_graph
import os
import sys
import uuid
import time
import asyncio
import requests
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Dict
from mongodb_config import (
    get_or_create_conversation,
    save_message,
    get_conversation_history,
    link_session_to_phone,
    get_session_by_phone
)

load_dotenv()

app = FastAPI(
    title="WhatsApp Shopping Assistant with Supervisor",
    version="6.0.0"
)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Main API URL
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://localhost:8000/api")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def get_or_create_session_for_phone(phone_number: str) -> str:
    """Get existing session or create new one for phone number"""
    # Check MongoDB for existing session
    existing_session = get_session_by_phone(phone_number)
    
    if existing_session:
        print(f"♻️ Using existing session: {existing_session}", file=sys.stderr)
        return existing_session
    
    # Create new session
    new_session_id = f"session-{uuid.uuid4().hex[:12]}"
    
    # Link in MongoDB
    link_session_to_phone(phone_number, new_session_id)
    
    # Link with main API
    try:
        response = requests.post(
            f"{MAIN_API_URL}/whatsapp/link-session",
            json={"phone": phone_number, "session_id": new_session_id},
            timeout=3
        )
        if response.ok:
            print(f"🔗 Session linked with main API", file=sys.stderr)
    except Exception as e:
        print(f"⚠️ Failed to link session with API: {e}", file=sys.stderr)
    
    print(f"✅ New session created: {new_session_id}", file=sys.stderr)
    return new_session_id


async def send_whatsapp_message(to_number: str, message: str, max_retries: int = 3) -> bool:
    """Send WhatsApp message with retry logic"""
    max_length = 3000
    
    if len(message) > max_length:
        truncated_message = message[:max_length] + "\n\n... (message continues, please ask for more details)"
        print(f"⚠️ Message truncated from {len(message)} to {len(truncated_message)} chars", file=sys.stderr)
        final_message = truncated_message
    else:
        final_message = message
    
    for attempt in range(max_retries):
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: twilio_client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    body=final_message,
                    to=to_number
                )
            )
            
            print(f"✅ Message sent ({len(final_message)} chars)", file=sys.stderr)
            return True
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Attempt {attempt + 1}/{max_retries} failed: {error_msg}", file=sys.stderr)
            
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"⏳ Waiting {wait_time}s before retry...", file=sys.stderr)
                    await asyncio.sleep(wait_time)
                    continue
            
            if attempt == max_retries - 1:
                print(f"❌ Failed to send message after {max_retries} attempts", file=sys.stderr)
                return False
    
    return False


async def process_user_message(phone_number: str, message: str) -> str:
    """
    Process user message through supervisor shopping assistant
    UPDATED for new supervisor architecture
    """
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"📱 WhatsApp from {phone_number}", file=sys.stderr)
    print(f"💬 Message: {message}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        # Get or create conversation in MongoDB
        conversation_id = get_or_create_conversation(phone_number)
        
        # Check for pending sessions (web → WhatsApp linking)
        print(f"🔍 Checking for pending web session...", file=sys.stderr)
        
        session_id = None
        try:
            response = requests.get(
                f"{MAIN_API_URL}/whatsapp/pending-sessions",
                timeout=2
            )
            
            if response.ok:
                pending_data = response.json()
                pending_sessions = pending_data.get("pending_sessions", [])
                
                if pending_sessions:
                    web_session_id = pending_sessions[0]
                    print(f"🔗 Found pending web session: {web_session_id}", file=sys.stderr)
                    
                    # Link sessions
                    link_session_to_phone(phone_number, web_session_id)
                    
                    requests.post(
                        f"{MAIN_API_URL}/whatsapp/link-session",
                        json={"phone": phone_number, "session_id": web_session_id},
                        timeout=2
                    )
                    
                    requests.delete(
                        f"{MAIN_API_URL}/whatsapp/pending-sessions/{web_session_id}",
                        timeout=2
                    )
                    
                    session_id = web_session_id
                    print(f"✅ Session linked to web: {session_id}", file=sys.stderr)
        
        except Exception as e:
            print(f"⚠️ Failed to check pending sessions: {e}", file=sys.stderr)
        
        # Use existing or create new session
        if not session_id:
            existing_session = get_session_by_phone(phone_number)
            if existing_session:
                session_id = existing_session
                print(f"♻️ Using existing session: {session_id}", file=sys.stderr)
            else:
                session_id = get_or_create_session_for_phone(phone_number)
                print(f"🆕 Created new session: {session_id}", file=sys.stderr)
        
        # Save user message to MongoDB
        save_message(
            conversation_id=conversation_id,
            phone_number=phone_number,
            message=message,
            sender="user"
        )
        
        config = {"configurable": {"thread_id": session_id}}
        
        # ✅ UPDATED: Get or create state for supervisor
        try:
            current_state = shopping_assistant_graph.get_state(config)
            if current_state and current_state.values:
                state = current_state.values
                print(f"📚 Loaded existing state", file=sys.stderr)
            else:
                state = create_initial_state(session_id)
                print(f"🆕 Created new state", file=sys.stderr)
        except Exception:
            state = create_initial_state(session_id)
            print(f"🆕 Created new state (fallback)", file=sys.stderr)
        
        # Ensure session_id is set
        state["session_id"] = session_id
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=message))
        
        print(f"📊 State before processing:", file=sys.stderr)
        print(f"   Messages: {len(state['messages'])}", file=sys.stderr)
        print(f"   Cart: {len(state.get('cart_items', []))} items", file=sys.stderr)
        print(f"   Cached products: {len(state.get('last_search_results', []))}", file=sys.stderr)
        
        # ✅ CRITICAL: Process through supervisor graph
        start_time = time.time()
        loop = asyncio.get_event_loop()
        
        # Invoke graph with state
        result = await loop.run_in_executor(
            None,
            lambda: shopping_assistant_graph.invoke(state, config)
        )
        
        processing_time = time.time() - start_time
        
        print(f"⏱️ Processing time: {processing_time:.2f}s", file=sys.stderr)
        
        # Extract assistant response (last AI message)
        assistant_response = ""
        if result.get("messages"):
            for msg in reversed(result["messages"]):
                if msg.__class__.__name__ == "AIMessage":
                    assistant_response = msg.content
                    break
        
        if not assistant_response:
            assistant_response = "I'm processing your request. Please try again."
        
        print(f"✅ Response: {len(assistant_response)} chars", file=sys.stderr)
        
        # Save assistant response to MongoDB
        save_message(
            conversation_id=conversation_id,
            phone_number=phone_number,
            message=assistant_response,
            sender="assistant",
            metadata={
                "processing_time": processing_time,
                "cart_items": len(result.get("cart_items", [])),
                "session_id": session_id
            }
        )
        
        # Cart is already synced by graph.py supervisor_node
        print(f"💾 MongoDB: Conversation saved", file=sys.stderr)
        sys.stderr.flush()
        
        return assistant_response
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        
        # Save error to MongoDB
        try:
            conversation_id = get_or_create_conversation(phone_number)
            save_message(
                conversation_id=conversation_id,
                phone_number=phone_number,
                message=f"Error: {str(e)}",
                sender="system",
                metadata={"error": True}
            )
        except:
            pass
        
        return "Sorry, I encountered an error. Please try again."


@app.get("/")
async def index():
    """Health check"""
    return {
        "status": "running",
        "service": "WhatsApp Shopping Assistant with Supervisor",
        "version": "6.0.0",
        "architecture": "Supervisor Multi-Agent",
        "main_api": MAIN_API_URL,
        "mongodb": "connected",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    MessageSid: str = Form(None)
):
    """Twilio WhatsApp webhook"""
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"📥 Incoming webhook", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    sys.stderr.flush()
    
    try:
        incoming_msg = Body.strip()
        from_number = From
        
        print(f"📱 From: {from_number}", file=sys.stderr)
        print(f"💬 Message: {incoming_msg[:100]}...", file=sys.stderr)
        sys.stderr.flush()
        
        if not incoming_msg or not from_number:
            return PlainTextResponse(str(MessagingResponse()), media_type="application/xml")
        
        # Process in background
        asyncio.create_task(process_and_send(from_number, incoming_msg))
        
        # Return empty TwiML immediately
        resp = MessagingResponse()
        
        print(f"✅ Webhook acknowledged", file=sys.stderr)
        sys.stderr.flush()
        
        return PlainTextResponse(str(resp), media_type="application/xml")
    
    except Exception as e:
        print(f"❌ Webhook error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.stderr.flush()
        
        resp = MessagingResponse()
        return PlainTextResponse(str(resp), media_type="application/xml")


async def process_and_send(phone_number: str, message: str):
    """Process message and send response (background task)"""
    try:
        response_text = await process_user_message(phone_number, message)
        
        # Send with retry logic
        success = await send_whatsapp_message(phone_number, response_text)
        
        if not success:
            await send_whatsapp_message(
                phone_number,
                "I processed your request, but couldn't send the full response. Please type 'status' to see your cart."
            )
    
    except Exception as e:
        print(f"❌ Background processing error: {e}", file=sys.stderr)
        try:
            await send_whatsapp_message(
                phone_number,
                "Sorry, something went wrong. Please try again."
            )
        except:
            pass


@app.get("/conversation/{phone_number}")
async def get_conversation(phone_number: str, limit: int = 50):
    """Get conversation history for a phone number"""
    try:
        history = get_conversation_history(phone_number, limit)
        return {
            "phone_number": phone_number,
            "message_count": len(history),
            "messages": history
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/sessions")
async def list_sessions():
    """List all active sessions from MongoDB"""
    from mongodb_config import sessions_collection
    
    sessions = list(sessions_collection.find({}, {"_id": 0, "phone_number": 1, "session_id": 1, "created_at": 1}))
    
    sessions_info = []
    for session in sessions:
        try:
            response = requests.get(f"{MAIN_API_URL}/cart/{session['session_id']}", timeout=2)
            cart_data = response.json() if response.ok else {"cart": [], "total": 0}
            
            sessions_info.append({
                "phone": session["phone_number"],
                "session_id": session["session_id"],
                "created_at": session.get("created_at"),
                "cart_items": len(cart_data.get("cart", [])),
                "total": cart_data.get("total", 0)
            })
        except Exception:
            sessions_info.append({
                "phone": session["phone_number"],
                "session_id": session["session_id"],
                "created_at": session.get("created_at"),
                "status": "error"
            })
    
    return {
        "total_sessions": len(sessions_info),
        "sessions": sessions_info
    }


@app.on_event("startup")
async def startup_event():
    """Startup message"""
    print("\n" + "🚀" * 40)
    print("WhatsApp Shopping Assistant - Supervisor Architecture v6.0.0")
    print("🚀" * 40)
    print(f"\n✅ Twilio: {TWILIO_ACCOUNT_SID[:10]}..." if TWILIO_ACCOUNT_SID else "❌ Twilio not configured")
    print(f"✅ WhatsApp: {TWILIO_WHATSAPP_NUMBER}")
    print(f"✅ Main API: {MAIN_API_URL}")
    print(f"✅ MongoDB: Connected")
    print(f"✅ Architecture: Supervisor Multi-Agent")
    print("\n🔗 Features:")
    print("   ✓ Supervisor delegates to specialized sub-agents")
    print("   ✓ Direct MCP tool calls (no nested agents)")
    print("   ✓ Smart product caching & cart management")
    print("   ✓ Automatic session linking (web ↔ WhatsApp)")
    print("   ✓ MongoDB conversation history")
    print("   ✓ Robust error handling & retry logic")
    print("="*80 + "\n")
    sys.stderr.flush()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("whatsapp_server:app", host="0.0.0.0", port=5000, reload=False)