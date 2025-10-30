"""
Test suite for the LangGraph shopping assistant.
Tests all agents and workflows without WhatsApp integration.
"""
import uuid
from datetime import datetime
from langchain_core.messages import HumanMessage
from state import create_initial_state
from graph import shopping_assistant_graph


def print_separator(title: str = ""):
    """Print a visual separator for test output."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def print_conversation(state):
    """Pretty print the conversation history."""
    print("\n💬 CONVERSATION HISTORY:")
    print("-" * 80)
    for msg in state["messages"]:
        role = "🧑 User" if msg.__class__.__name__ == "HumanMessage" else "🤖 Assistant"
        print(f"\n{role}:")
        print(f"  {msg.content}")
    print("-" * 80)


def run_conversation(session_id: str, user_messages: list[str]):
    """
    Simulate a conversation with multiple user messages.
    
    Args:
        session_id: Unique session identifier
        user_messages: List of user messages to send
    """
    print_separator(f"Starting Conversation: {session_id}")
    
    config = {"configurable": {"thread_id": session_id}}
    
    # Initialize the state using update_state
    shopping_assistant_graph.update_state(config, create_initial_state(session_id))
    
    state = None
    
    # Process each user message
    for i, user_msg in enumerate(user_messages):
        print(f"\n\n📨 User Message #{i+1}: {user_msg}")
        
        # Prepare input
        input_data = {"messages": [HumanMessage(content=user_msg)]}
        
        # Invoke the graph
        try:
            result = shopping_assistant_graph.invoke(input_data, config)
            state = result  # Update state with result
            
            # Show the latest assistant response
            if state["messages"]:
                last_msg = state["messages"][-1]
                if last_msg.__class__.__name__ != "HumanMessage":
                    print(f"\n🤖 Assistant Response:")
                    print(f"  {last_msg.content}")
            
            # Show current state info
            print(f"\n📊 State Info:")
            print(f"  - Intent: {state.get('current_intent', 'N/A')}")
            print(f"  - Cart Items: {len(state.get('cart_items', []))}")
            print(f"  - Awaiting Confirmation: {state.get('awaiting_confirmation', False)}")
            
        except Exception as e:
            print(f"\n❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
    
    # Print full conversation at the end
    if state:
        print_conversation(state)
    
    return state


# ============================================================================
# TEST CASES
# ============================================================================

def test_1_greeting():
    """Test Case 1: Simple greeting and general conversation."""
    print_separator("TEST 1: Greeting and General Conversation")
    
    messages = [
        "Hello!",
        "What can you help me with?",
        "Thanks!"
    ]
    
    run_conversation("test-greeting-001", messages)


def test_2_product_search():
    """Test Case 2: Product search workflow."""
    print_separator("TEST 2: Product Search")
    
    messages = [
        "Hi, I'm looking for a silver watch",
        "Show me watches under $150",
        "Tell me more about the first one"
    ]
    
    run_conversation("test-search-001", messages)


def test_3_product_search_with_filters():
    """Test Case 3: Product search with specific filters."""
    print_separator("TEST 3: Product Search with Filters")
    
    messages = [
        "I need a brown leather belt",
        "Show me wallets in black color",
        "Any formal shoes available?"
    ]
    
    run_conversation("test-search-filters-001", messages)


def test_4_checkout_flow():
    """Test Case 4: Complete checkout workflow."""
    print_separator("TEST 4: Checkout Flow")
    
    messages = [
        "Show me watches under $130",
        "I'd like to buy the Chronograph Watch",
        "My name is John Doe, email is john.doe@example.com, phone is +1-555-0123",
        "Yes, please confirm the order"
    ]
    
    state = run_conversation("test-checkout-001", messages)
    
    # Note: This test requires manual setup of cart items
    # In production, the search agent would add items to cart
    print("\n⚠️ Note: For checkout to work, products need to be added to cart by search agent")


def test_5_order_tracking():
    """Test Case 5: Order tracking workflow."""
    print_separator("TEST 5: Order Tracking")
    
    messages = [
        "I want to track my order",
        "My email is john.doe@example.com",
        "Can you check order status?"
    ]
    
    run_conversation("test-tracking-001", messages)


def test_6_full_shopping_journey():
    """Test Case 6: Complete end-to-end shopping journey."""
    print_separator("TEST 6: Full Shopping Journey")
    
    messages = [
        "Hello! I'm looking for accessories",
        "Show me leather wallets under $50",
        "I like the bifold wallet. What colors do you have?",
        "Great! I'll take the black one",
        "My name is Jane Smith, email jane.smith@example.com, phone +1-555-9999",
        "Yes, proceed with the order",
        "Thank you! Can I track this order?",
        "What's the status of my order?"
    ]
    
    run_conversation("test-full-journey-001", messages)


def test_7_price_range_search():
    """Test Case 7: Search with price constraints."""
    print_separator("TEST 7: Price Range Search")
    
    messages = [
        "What shoes do you have under $80?",
        "Show me watches between $100 and $150",
        "Any belts under $50?"
    ]
    
    run_conversation("test-price-range-001", messages)


def test_8_multi_intent():
    """Test Case 8: Multiple intents in one conversation."""
    print_separator("TEST 8: Multiple Intents")
    
    messages = [
        "Hi, show me formal shoes",
        "Actually, let me first check my previous order status",
        "Email is test@example.com",
        "Okay, now back to shoes - show me black formal shoes",
        "I'll think about it, thanks!"
    ]
    
    run_conversation("test-multi-intent-001", messages)


def test_9_error_handling():
    """Test Case 9: Error handling and edge cases."""
    print_separator("TEST 9: Error Handling")
    
    messages = [
        "Show me products that don't exist like zzzzzz",
        "Track order number 999999999",
        "I want to buy something but I won't provide details",
    ]
    
    run_conversation("test-error-handling-001", messages)


def test_10_color_and_family_filters():
    """Test Case 10: Search with color and category filters."""
    print_separator("TEST 10: Color and Category Filters")
    
    messages = [
        "Show me all black accessories",
        "What about brown footwear?",
        "Do you have any blue watches?",
        "Show me everything in the Accessories family"
    ]
    
    run_conversation("test-filters-001", messages)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all test cases."""
    print("\n" + "🧪" * 40)
    print("LANGGRAPH SHOPPING ASSISTANT - TEST SUITE")
    print("🧪" * 40)
    
    tests = [
        ("Greeting & General", test_1_greeting),
        ("Product Search", test_2_product_search),
        ("Search with Filters", test_3_product_search_with_filters),
        ("Checkout Flow", test_4_checkout_flow),
        ("Order Tracking", test_5_order_tracking),
        ("Full Shopping Journey", test_6_full_shopping_journey),
        ("Price Range Search", test_7_price_range_search),
        ("Multiple Intents", test_8_multi_intent),
        ("Error Handling", test_9_error_handling),
        ("Color & Category Filters", test_10_color_and_family_filters),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n\n{'='*80}")
            print(f"Running: {test_name}")
            print('='*80)
            test_func()
            passed += 1
            print(f"\n✅ {test_name} - PASSED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} - FAILED")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(tests)}")
    print("="*80)


def run_interactive_mode():
    """Run in interactive mode for manual testing."""
    print("\n" + "🎮" * 40)
    print("INTERACTIVE MODE - Chat with the Shopping Assistant")
    print("Type 'quit' or 'exit' to stop")
    print("🎮" * 40)
    
    session_id = f"interactive-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": session_id}}
    
    # Initialize the state using update_state
    shopping_assistant_graph.update_state(config, create_initial_state(session_id))
    
    print("\n🤖 Assistant: Hello! I'm your AI shopping assistant. How can I help you today?")
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Assistant: Thank you for shopping with us! Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            # Prepare input
            input_data = {"messages": [HumanMessage(content=user_input)]}
            
            # Process through graph
            result = shopping_assistant_graph.invoke(input_data, config)
            
            # Show assistant response
            if result["messages"]:
                last_msg = result["messages"][-1]
                if last_msg.__class__.__name__ != "HumanMessage":
                    print(f"\n🤖 Assistant: {last_msg.content}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    print("\n🚀 WhatsApp AI Shopping Assistant - Test Suite")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Run all automated tests")
    print("  2. Run interactive mode (chat manually)")
    print("  3. Run specific test")
    print("=" * 80)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = input("\nSelect mode (1/2/3): ").strip()
    
    if mode == "1":
        run_all_tests()
    elif mode == "2":
        run_interactive_mode()
    elif mode == "3":
        print("\nAvailable tests:")
        print("  1. Greeting")
        print("  2. Product Search")
        print("  3. Search with Filters")
        print("  4. Checkout Flow")
        print("  5. Order Tracking")
        print("  6. Full Shopping Journey")
        print("  7. Price Range Search")
        print("  8. Multiple Intents")
        print("  9. Error Handling")
        print("  10. Color & Category Filters")
        
        test_num = input("\nSelect test number: ").strip()
        
        tests = {
            "1": test_1_greeting,
            "2": test_2_product_search,
            "3": test_3_product_search_with_filters,
            "4": test_4_checkout_flow,
            "5": test_5_order_tracking,
            "6": test_6_full_shopping_journey,
            "7": test_7_price_range_search,
            "8": test_8_multi_intent,
            "9": test_9_error_handling,
            "10": test_10_color_and_family_filters,
        }
        
        if test_num in tests:
            tests[test_num]()
        else:
            print("❌ Invalid test number")
    else:
        print("❌ Invalid mode. Use 1, 2, or 3")