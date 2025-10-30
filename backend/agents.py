"""
SUPERVISOR MULTI-AGENT ARCHITECTURE - SMART ORDER TRACKING
====================================
Agent remembers recent order numbers and user email
"""
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from mcp_client import get_mcp_tools
import sys
import json
import re
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# ============================================================================
# MCP TOOLS INITIALIZATION
# ============================================================================

print("\n🛠️ Initializing MCP Tools...", file=sys.stderr)
mcp_tools = get_mcp_tools(auto_start_server=False)

catalog_search = next((t for t in mcp_tools if t.name == "catalog_search"), None)
get_product_details = next((t for t in mcp_tools if t.name == "get_product_details"), None)
get_product_by_name = next((t for t in mcp_tools if t.name == "get_product_by_name"), None)
create_customer_order = next((t for t in mcp_tools if t.name == "create_customer_order"), None)
lookup_order_status = next((t for t in mcp_tools if t.name == "lookup_order_status"), None)
manage_cart = next((t for t in mcp_tools if t.name == "manage_cart"), None)

all_loaded = all([catalog_search, get_product_details, get_product_by_name, 
                  create_customer_order, lookup_order_status, manage_cart])
if all_loaded:
    print("✅ All MCP tools loaded successfully!\n", file=sys.stderr)


# ============================================================================
# SHARED STATE MANAGEMENT
# ============================================================================

class SharedAgentState:
    """Shared state accessible by all sub-agents"""
    def __init__(self):
        self.last_search_results = []
        self.cart_items = []
        self.session_id = ""
        self.user_name = ""
        self.user_email = ""
        self.user_phone = ""
        self.conversation_mode = "browsing"  # browsing, cart, checkout_pending, tracking
        self.last_order_number = None  # Store last created order number
        self.last_order_email = None  # Store email used for last order

shared_state = SharedAgentState()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_products_from_tool_response(tool_response: str) -> List[Dict]:
    """Extract product list from MCP catalog_search response"""
    try:
        if isinstance(tool_response, str):
            parsed = json.loads(tool_response)
            if isinstance(parsed, list):
                return parsed
            elif isinstance(parsed, dict):
                return parsed.get("results", parsed.get("products", []))
        elif isinstance(tool_response, list):
            return tool_response
        return []
    except Exception as e:
        print(f"❌ Error extracting products: {e}", file=sys.stderr)
        return []


def parse_cart_command(command: str) -> Dict[str, Any]:
    """Parse natural language cart commands into structured data"""
    command = command.lower().strip()
    
    if "add" in command:
        action = "add"
        match = re.search(r'(\d+)', command)
        position = int(match.group(1)) if match else None
        return {"action": action, "product_position": position}
    
    elif "view" in command or "show" in command:
        return {"action": "view"}
    
    elif "remove" in command or "delete" in command:
        action = "remove"
        match = re.search(r'(\d+)', command)
        position = int(match.group(1)) if match else None
        return {"action": action, "product_position": position}
    
    elif "clear" in command or "empty" in command:
        return {"action": "clear"}
    
    else:
        return {"action": "view"}


def parse_contact_info(text: str) -> Optional[Dict[str, str]]:
    """
    Parse contact information from user message
    
    Formats:
    - "John Doe, john@email.com, +1234567890"
    - "roni, roni@gmail.com, 0314580109"
    """
    # Remove extra quotes and clean
    text = text.strip().strip("'\"")
    
    # Check if it contains email (basic validation)
    if '@' not in text or ',' not in text:
        return None
    
    # Split by comma
    parts = [p.strip().strip("'\"") for p in text.split(',')]
    
    if len(parts) >= 3:
        return {
            "name": parts[0],
            "email": parts[1],
            "phone": parts[2]
        }
    
    return None


# ============================================================================
# SUB-AGENT IMPLEMENTATIONS
# ============================================================================

def search_agent_tool(query: str) -> str:
    """🔍 Search Agent - Finds products with smart categorization"""
    print(f"\n🔍 Search Agent executing: '{query}'", file=sys.stderr)
    print(f"   Session: {shared_state.session_id}", file=sys.stderr)
    
    # Update conversation mode
    shared_state.conversation_mode = "browsing"
    
    query_lower = query.lower().strip()
    query_lower = query_lower.replace("show all", "").replace("show me", "").replace("i want", "").replace("just", "").strip()
    
    words = query_lower.split()
    has_color = any(color in query_lower for color in ['silver', 'black', 'brown', 'white', 'blue', 'red', 'gold', 'navy', 'tan', 'green', 'grey', 'gray'])
    has_price = any(price_word in query_lower for price_word in ['under', 'below', 'cheap', 'expensive', 'price'])
    is_specific_request = has_color or has_price or len(words) > 2
    
    generic_keywords = {
        'watch': 'Watches',
        'watches': 'Watches',
        'belt': 'Accessories',
        'belts': 'Accessories',
        'wallet': 'Accessories',
        'wallets': 'Accessories',
        'shoe': 'Footwear',
        'shoes': 'Footwear',
        'footwear': 'Footwear',
        'footwears': 'Footwear'
    }
    
    is_generic = False
    target_category = None
    
    for keyword, category in generic_keywords.items():
        if keyword == query_lower:
            is_generic = True
            target_category = category
            break
    
    try:
        if 'watch' in query_lower:
            base_query = 'watch'
        elif 'shoe' in query_lower or 'footwear' in query_lower:
            base_query = 'shoe'
        elif 'belt' in query_lower:
            base_query = 'belt'
        elif 'wallet' in query_lower:
            base_query = 'wallet'
        else:
            base_query = words[0].rstrip('s') if words else query
        
        raw_response = catalog_search.func(query=base_query)
        products = extract_products_from_tool_response(raw_response)
        
        if products:
            if target_category:
                products = [p for p in products if p.get('family') == target_category]
            
            for color in ['silver', 'black', 'brown', 'white', 'blue', 'red', 'gold', 'navy', 'tan', 'green', 'grey', 'gray']:
                if color in query.lower():
                    color_filtered = [p for p in products if color.lower() in p.get('color', '').lower()]
                    if color_filtered:
                        products = color_filtered
                    break
        
        if is_generic and not is_specific_request and products:
            category_name = products[0].get('family', 'products')
            colors_set = set(p.get('color', '') for p in products if p.get('color'))
            
            response = f"Great! I found several types of {category_name.lower()}:\n\n"
            response += "**Popular Colors:**\n"
            for color in sorted(list(colors_set)[:4]):
                response += f"• {color} {category_name.lower()}\n"
            response += f"\n💡 Say **\"{list(colors_set)[0]} {category_name.lower()}\"** to see options!"
            
            shared_state.last_search_results = products[:5]
            return response
        
        if products:
            shared_state.last_search_results = products[:5]
        else:
            shared_state.last_search_results = []
            return "Hmm, I couldn't find that. Try being more specific! 🔍"
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        shared_state.last_search_results = []
        return "Sorry, search error. Please try again! 😊"
    
    if not shared_state.last_search_results:
        return "No products found. Try different keywords! 🔍"
    
    format_prompt = f"""Format these products conversationally.

**PRODUCTS:**
{json.dumps(shared_state.last_search_results[:3], indent=2)}

**FORMAT:**
Here are 3 great [category] for you:

1️⃣ **[Name]** - $[price]
   [Very short description - max 10 words]
   ![Product]([image_url])

2️⃣ **[Name]** - $[price]
   [Very short description - max 10 words]
   ![Product]([image_url])

3️⃣ **[Name]** - $[price]
   [Very short description - max 10 words]
   ![Product]([image_url])

💡 Like one? Say "add option X" to add to cart!

RULES: Max 10 words per description."""
    
    try:
        response = llm.invoke(format_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    except:
        response = f"Found {len(shared_state.last_search_results)} options:\n\n"
        for i, p in enumerate(shared_state.last_search_results[:3], 1):
            response += f"{i}. {p.get('name')} - ${p.get('price', 0):.2f}\n"
        response += "\nSay 'add option X' to add to cart!"
        return response


def cart_agent_tool(command: str) -> str:
    """🛒 Cart Agent - Manages shopping cart operations"""
    print(f"\n🛒 Cart Agent executing: '{command}'", file=sys.stderr)
    print(f"   Session: {shared_state.session_id}", file=sys.stderr)
    
    # Update conversation mode
    shared_state.conversation_mode = "cart"
    
    parsed = parse_cart_command(command)
    action = parsed.get("action", "view")
    product_position = parsed.get("product_position")
    
    print(f"   Parsed: action={action}, position={product_position}", file=sys.stderr)
    
    if action == "add":
        if not shared_state.last_search_results:
            return "🛒 Please search for products first!"
        
        if not product_position or product_position < 1 or product_position > len(shared_state.last_search_results):
            return f"❌ Invalid option. Please choose 1-{len(shared_state.last_search_results)}."
    
    try:
        cart_result = manage_cart.func(
            action=action,
            session_id=shared_state.session_id,
            product_position=product_position,
            product_id=None,
            quantity=1,
            last_search_results=shared_state.last_search_results
        )
        
        if isinstance(cart_result, str):
            cart_data = json.loads(cart_result)
        else:
            cart_data = cart_result
        
        if cart_data.get("success"):
            shared_state.cart_items = cart_data.get("cart_items", [])
            
            if action == "add":
                product_name = cart_data.get("cart_items", [{}])[-1].get("name", "Product")
                response = f"✅ **Added {product_name} to cart!**\n\n"
            else:
                response = ""
            
            response += "🛒 **Your Cart:**\n\n"
            
            if shared_state.cart_items:
                total = 0
                for item in shared_state.cart_items:
                    name = item.get("name", "Unknown")
                    price = item.get("price", 0)
                    qty = item.get("quantity", 1)
                    response += f"• **{name}** - ${price:.2f} × {qty}\n"
                    total += price * qty
                
                response += f"\n💰 **Total: ${total:.2f}**\n\n"
                response += "Ready to checkout? 🎉"
            else:
                response += "Your cart is empty!\n\nLet's find something great! 🛍️"
            
            return response
        else:
            error_msg = cart_data.get("error", "Unknown error")
            return f"❌ Cart operation failed: {error_msg}"
    
    except Exception as e:
        print(f"❌ Cart error: {e}", file=sys.stderr)
        return f"❌ Sorry, cart operation failed."


def checkout_agent_tool(command: str) -> str:
    """💳 Checkout Agent - Handles order placement"""
    print(f"\n💳 Checkout Agent executing: '{command}'", file=sys.stderr)
    print(f"   Session: {shared_state.session_id}", file=sys.stderr)
    
    if not shared_state.cart_items:
        return "🛒 Your cart is empty! Let me help you find something great."
    
    command_lower = command.lower().strip()
    
    # Check if confirmation
    is_confirm = any(word in command_lower for word in ['yes', 'confirm', 'proceed', 'ok', 'place order'])
    
    # Try to parse contact info
    contact_info = parse_contact_info(command)
    if contact_info:
        shared_state.user_name = contact_info["name"]
        shared_state.user_email = contact_info["email"]
        shared_state.user_phone = contact_info["phone"]
        print(f"   Parsed contact: {contact_info}", file=sys.stderr)
    
    # Phase 1: Collect information
    if not all([shared_state.user_name, shared_state.user_email, shared_state.user_phone]):
        shared_state.conversation_mode = "checkout_pending"
        
        missing = []
        if not shared_state.user_name: missing.append("📝 Full Name")
        if not shared_state.user_email: missing.append("📧 Email Address")
        if not shared_state.user_phone: missing.append("📱 Phone Number")
        
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in shared_state.cart_items)
        
        response = "Great! Let's complete your order 🎉\n\n"
        response += f"**Your Cart:** {len(shared_state.cart_items)} item(s) - ${total:.2f}\n\n"
        response += "To proceed, I need:\n\n"
        response += f"{chr(10).join(missing)}\n\n"
        response += 'Provide like:\n"John Doe, john@email.com, +1234567890"'
        
        return response
    
    # Phase 2: Show confirmation
    if not is_confirm:
        shared_state.conversation_mode = "checkout_pending"
        
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in shared_state.cart_items)
        
        # Mask PII for display
        email_parts = shared_state.user_email.split("@")
        masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}" if len(email_parts) == 2 else shared_state.user_email
        masked_phone = f"***{shared_state.user_phone[-4:]}" if len(shared_state.user_phone) >= 4 else shared_state.user_phone
        
        response = "📋 **Order Confirmation**\n\n"
        response += "**Items:**\n"
        for item in shared_state.cart_items:
            response += f"• {item.get('name')} - ${item.get('price', 0):.2f} × {item.get('quantity', 1)}\n"
        
        response += f"\n💵 **Total: ${total:.2f}**\n\n"
        response += "**Delivery Details:**\n"
        response += f"👤 Name: {shared_state.user_name}\n"
        response += f"📧 Email: {masked_email}\n"
        response += f"📱 Phone: {masked_phone}\n\n"
        response += "Say 'Yes' or 'Confirm' to complete your order ✅"
        
        return response
    
    # Phase 3: Create order
    try:
        print(f"📞 Creating order in Salesforce...", file=sys.stderr)
        print(f"   Name: {shared_state.user_name}", file=sys.stderr)
        print(f"   Email: {shared_state.user_email}", file=sys.stderr)
        print(f"   Phone: {shared_state.user_phone}", file=sys.stderr)
        
        actual_total = sum(item.get("price", 0) * item.get("quantity", 1) for item in shared_state.cart_items)
        
        items = []
        for item in shared_state.cart_items:
            items.append({
                "pricebook_entry_id": item.get("pricebook_entry_id"),
                "quantity": item.get("quantity", 1),
                "unit_price": item.get("price", 0.0)
            })
        
        order_result = create_customer_order.func(
            customer_name=shared_state.user_name,
            customer_email=shared_state.user_email,
            customer_phone=shared_state.user_phone,
            items=items,
            checkout_source="WhatsApp Bot"
        )
        
        if isinstance(order_result, str):
            order_data = json.loads(order_result)
        else:
            order_data = order_result
        
        print(f"📊 Order result: {json.dumps(order_data, indent=2)[:200]}", file=sys.stderr)
        
        if order_data.get("success"):
            # Store order info for future tracking
            order_number = order_data.get('order_number')
            shared_state.last_order_number = order_number
            shared_state.last_order_email = shared_state.user_email
            
            print(f"💾 Stored order info: #{order_number}, {shared_state.user_email}", file=sys.stderr)
            
            # Clear cart and personal info (but keep order reference)
            shared_state.cart_items = []
            shared_state.user_name = ""
            shared_state.user_email = ""
            shared_state.user_phone = ""
            shared_state.conversation_mode = "browsing"
            
            return f"""🎉 **Order Confirmed!**

✅ Order Number: #{order_number}
💵 Total: ${actual_total:.2f}

Your order will arrive in 3-5 business days! 🚚

Thanks for shopping! 😊

💡 You can track your order anytime by saying "track my order" or "order status"."""
        else:
            error_msg = order_data.get("error", "Unknown error")
            return f"❌ Order failed: {error_msg}\n\nPlease try again or contact support."
    
    except Exception as e:
        print(f"❌ Checkout error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return "❌ Sorry, checkout failed. Please try again."


def tracking_agent_tool(query: str) -> str:
    """📦 Tracking Agent - Looks up order status with smart defaults"""
    print(f"\n📦 Tracking Agent executing: '{query}'", file=sys.stderr)
    print(f"   Last order: #{shared_state.last_order_number}", file=sys.stderr)
    print(f"   Last email: {shared_state.last_order_email}", file=sys.stderr)
    
    shared_state.conversation_mode = "tracking"
    
    order_number = None
    customer_email = None
    
    # Try to extract from query
    if '@' in query:
        customer_email = query.strip()
    elif '#' in query:
        order_number = query.replace('#', '').strip()
    elif query.isdigit():
        order_number = query.strip()
    
    # SMART DEFAULT: If no order info provided but we have recent order
    if not order_number and not customer_email:
        if shared_state.last_order_number:
            print(f"💡 Using remembered order: #{shared_state.last_order_number}", file=sys.stderr)
            order_number = shared_state.last_order_number
        elif shared_state.last_order_email:
            print(f"💡 Using remembered email: {shared_state.last_order_email}", file=sys.stderr)
            customer_email = shared_state.last_order_email
        else:
            return "To track your order, provide:\n• Order number (e.g., #00000123)\n• OR your email"
    
    try:
        tracking_result = lookup_order_status.func(
            order_number=order_number,
            customer_email=customer_email
        )
        
        if isinstance(tracking_result, str):
            tracking_data = json.loads(tracking_result)
        else:
            tracking_data = tracking_result
        
        if tracking_data.get("success"):
            status = tracking_data.get("status", "Unknown")
            
            response = f"""📦 **Order Status**

📄 Order: #{tracking_data.get('order_number')}
📅 Date: {tracking_data.get('order_date')}
✅ Status: **{status}**

**Items:**
"""
            
            for item in tracking_data.get("items", []):
                response += f"• {item.get('product_name')} × {item.get('quantity')}\n"
            
            response += f"\n💵 Total: ${tracking_data.get('total_amount', 0):.2f}\n"
            response += "Expected delivery: 3-5 business days"
            
            return response
        else:
            return "❌ Order not found. Check the order number/email."
    
    except Exception as e:
        print(f"❌ Tracking error: {e}", file=sys.stderr)
        return "❌ Couldn't retrieve order status."


# ============================================================================
# CREATE SUB-AGENT TOOLS
# ============================================================================

search_tool = Tool(
    name="search_products",
    func=search_agent_tool,
    description="Search for products. Input: search query like 'watches' or 'silver watches under $150'"
)

cart_tool = Tool(
    name="manage_cart",
    func=cart_agent_tool,
    description="Manage cart. Input: 'add option 1' or 'add 1' to add first product, 'view' to see cart, 'remove 2' to remove item"
)

checkout_tool = Tool(
    name="checkout_order",
    func=checkout_agent_tool,
    description="Handle checkout. Input: 'checkout' to start, 'Name, email, phone' for details, 'confirm' or 'yes' to finalize"
)

tracking_tool = Tool(
    name="track_order",
    func=tracking_agent_tool,
    description="Track order status. Input: order number, email, or just 'track order' to check most recent order"
)


# ============================================================================
# CONTEXT-AWARE QUERY HANDLER
# ============================================================================

def handle_contextual_query(message: str) -> Optional[str]:
    """
    Handle queries that depend on conversation context
    Returns the appropriate tool name if context-dependent
    """
    message_lower = message.lower().strip()
    
    # If in checkout flow and user says yes/confirm/proceed
    if shared_state.conversation_mode == "checkout_pending":
        if any(word in message_lower for word in ['yes', 'confirm', 'proceed', 'ok', 'place order']):
            print(f"💡 Context-aware: Interpreting '{message}' as checkout confirmation", file=sys.stderr)
            return "checkout_order"
    
    # If cart has items and user says checkout/buy/order
    if shared_state.cart_items and any(word in message_lower for word in ['checkout', 'buy', 'order', 'purchase']):
        return "checkout_order"
    
    # SMART TRACKING: If user asks about order status without specifics
    if any(phrase in message_lower for phrase in ['track my order', 'order status', 'where is my order', 'check my order', 'my order']):
        if shared_state.last_order_number or shared_state.last_order_email:
            print(f"💡 Smart tracking: Using remembered order info", file=sys.stderr)
            return "track_order"
    
    return None


def handle_simple_queries(message: str) -> Optional[str]:
    """Handle greetings without agent"""
    message_lower = message.lower().strip()
    
    if any(message_lower.startswith(p) for p in ['hi', 'hello', 'hey']):
        shared_state.conversation_mode = "browsing"
        return """Hey! 👋 I'm your shopping assistant!

I can help you:
🔍 Find products
🛒 Manage cart
✅ Checkout
📦 Track orders

What interests you?"""
    
    if any(p in message_lower for p in ['thanks', 'thank you']):
        return "You're welcome! Need anything else? 😊"
    
    if message_lower in ['help', 'options']:
        return """I can help you with:

🔍 Search: "Show me watches"
🛒 Cart: "Add option 2"
💳 Checkout: "Checkout"
📦 Track: "Track my order"

What would you like?"""
    
    return None


# ============================================================================
# SUPERVISOR AGENT
# ============================================================================

def create_supervisor_agent():
    """Create supervisor with ONE action per message"""
    
    react_prompt = PromptTemplate.from_template("""You are a shopping assistant. For each user message, take EXACTLY ONE action and return the result.

You have access to the following tools:

{tools}

IMPORTANT INSTRUCTIONS:
1. Take ONLY ONE action per user message
2. After getting the Observation, IMMEDIATELY go to "Final Answer"
3. DO NOT take a second action
4. Return the Observation result as the Final Answer without modifying it

Use this format:

Question: the input question you must answer
Thought: I should use a tool to help
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Thought: I have the information I need
Final Answer: [Return the Observation exactly as-is]

CRITICAL: After Observation, you MUST go directly to "Final Answer" - do NOT take another Action!

Begin!

Question: {input}
Thought:{agent_scratchpad}""")
    
    supervisor_tools = [search_tool, cart_tool, checkout_tool, tracking_tool]
    
    supervisor_agent = create_react_agent(llm, supervisor_tools, react_prompt)
    
    supervisor_executor = AgentExecutor(
        agent=supervisor_agent,
        tools=supervisor_tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=2,
        return_intermediate_steps=False
    )
    
    return supervisor_executor


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def invoke_supervisor(user_message: str, session_id: str, state: dict) -> str:
    """Main entry point"""
    print(f"\n{'='*80}", file=sys.stderr)
    print(f"🤖 Supervisor Processing", file=sys.stderr)
    print(f"   Session: {session_id}", file=sys.stderr)
    print(f"   Message: {user_message}", file=sys.stderr)
    print(f"   Mode: {shared_state.conversation_mode}", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)
    
    # Update shared state
    shared_state.session_id = session_id
    shared_state.cart_items = state.get("cart_items", [])
    shared_state.last_search_results = state.get("last_search_results", [])
    shared_state.user_name = state.get("user_name", "")
    shared_state.user_email = state.get("user_email", "")
    shared_state.user_phone = state.get("user_phone", "")
    
    # NEW: Load order memory from state
    shared_state.last_order_number = state.get("last_order_number")
    shared_state.last_order_email = state.get("last_order_email")
    
    # Handle simple queries first
    simple_response = handle_simple_queries(user_message)
    if simple_response:
        print(f"✅ Handled as simple query", file=sys.stderr)
        return simple_response
    
    # Check for context-aware shortcuts
    contextual_tool = handle_contextual_query(user_message)
    if contextual_tool:
        print(f"💡 Using context-aware tool: {contextual_tool}", file=sys.stderr)
        # Call the tool directly
        if contextual_tool == "checkout_order":
            return checkout_agent_tool(user_message)
        elif contextual_tool == "track_order":
            return tracking_agent_tool(user_message)
    
    # Create supervisor
    supervisor = create_supervisor_agent()
    
    # Invoke
    try:
        result = supervisor.invoke({"input": user_message})
        response = result['output']
        
        print(f"✅ Supervisor completed", file=sys.stderr)
        return response
    
    except Exception as e:
        print(f"❌ Supervisor error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return "Sorry, I encountered an error. Please try again."


print("✅ Supervisor Multi-Agent System Initialized", file=sys.stderr)
print(f"   🔍 Search Agent (with mode tracking)", file=sys.stderr)
print(f"   🛒 Cart Agent (with mode tracking)", file=sys.stderr)
print(f"   💳 Checkout Agent (stores order info)", file=sys.stderr)
print(f"   📦 Tracking Agent (SMART: remembers last order)", file=sys.stderr)
print(f"   🤖 Supervisor (context-aware, single action)", file=sys.stderr)