"""
Enhanced FastMCP Server with FIXED cart management and smart product positioning.
"""
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any
from datetime import datetime
from openai import OpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Salesforce functions
try:
    from salesforce.client import (
        list_active_products,
        get_standard_pricebook,
        upsert_account,
        create_order,
        create_order_item,
        get_order_status,
        sf
    )
    from salesforce.schema import Order, OrderItem
    SALESFORCE_AVAILABLE = True
    print("✅ Salesforce connection initialized", file=sys.stderr)
except ImportError as e:
    print(f"⚠️ Salesforce imports not available: {e}", file=sys.stderr)
    SALESFORCE_AVAILABLE = False

# Create FastMCP server
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001

mcp = FastMCP(
    name="shopping-assistant",
    host=SERVER_HOST,
    port=SERVER_PORT,
)

# Initialize OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
client = OpenAI()

# Query interpretation schema
class ProductQuery(BaseModel):
    query: str = Field(..., description="Main product keyword")
    category: Optional[str] = Field(None, description="Category like Footwear, Accessories, Watches")
    color: Optional[str] = Field(None, description="Color if mentioned")
    size: Optional[str] = Field(None, description="Size if mentioned")
    price_min: Optional[float] = Field(None, description="Minimum price")
    price_max: Optional[float] = Field(None, description="Maximum price")

parser = PydanticOutputParser(pydantic_object=ProductQuery)

prompt = PromptTemplate(
    template=(
        "Extract structured search filters from this query.\n\n"
        "User Query: {user_query}\n\n"
        "{format_instructions}\n"
    ),
    input_variables=["user_query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def interpret_search_query(user_query: str) -> dict:
    """Use LLM to extract structured filters."""
    try:
        chain_input = prompt.format_prompt(user_query=user_query)
        response = llm.invoke(chain_input.to_string())
        filters = parser.parse(response.content)
        return filters.dict()
    except Exception as e:
        return {
            "query": user_query,
            "category": None,
            "color": None,
            "size": None,
            "price_min": None,
            "price_max": None,
        }


@mcp.tool()
def catalog_search(
    query: str,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    color: Optional[str] = None,
    family: Optional[str] = None,
    size: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for products with AI-powered query interpretation.
    
    Returns: List of matching products (max 10 items)
    """
    if not SALESFORCE_AVAILABLE:
        return [{"error": "Salesforce connection not available"}]
    
    try:
        # Interpret query with AI if complex
        if query and len(query.split()) > 2:
            filters = interpret_search_query(query)
            query = filters.get("query")
            family = family or filters.get("category")
            color = color or filters.get("color")
            size = size or filters.get("size")
            min_price = min_price or filters.get("price_min")
            max_price = max_price or filters.get("price_max")
        
        # Build SOQL query with STRICT matching
        soql = """
        SELECT Id, Name, ProductCode, Description, Family, Color__c, Size__c, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE IsActive = true
        """
        
        conditions = []
        
        # CRITICAL FIX: Require ALL search terms to match (AND logic, not OR)
        if query:
            search_terms = query.lower().split()
            for term in search_terms:
                # Each term must appear in Name OR Description
                conditions.append(f"(Name LIKE '%{term}%' OR Description LIKE '%{term}%')")
        
        if color:
            conditions.append(f"Color__c LIKE '%{color}%'")
        
        if family:
            conditions.append(f"Family = '{family}'")
        
        if size:
            conditions.append(f"Size__c LIKE '%{size}%'")
        
        if conditions:
            soql += " AND " + " AND ".join(conditions)
        
        # Order by relevance (products with more matches first)
        soql += " ORDER BY Name ASC LIMIT 50"
        
        # Execute query
        results = sf.query(soql)
        
        # Format results
        products = []
        for record in results['records']:
            # Get price from pricebook entry
            price = None
            pricebook_entry_id = None
            if record.get('PricebookEntries') and record['PricebookEntries']['records']:
                price = record['PricebookEntries']['records'][0]['UnitPrice']
                pricebook_entry_id = record['PricebookEntries']['records'][0]['Id']
            
            # Apply price filters
            if min_price and price and price < min_price:
                continue
            if max_price and price and price > max_price:
                continue
            
            product = {
                "id": record['Id'],
                "name": record['Name'],
                "sku": record['ProductCode'],
                "description": record.get('Description', ''),
                "family": record.get('Family', ''),
                "color": record.get('Color__c', ''),
                "size": record.get('Size__c', ''),
                "price": price,
                "pricebook_entry_id": pricebook_entry_id,
                "image_url": record.get('Image_URL__c', ''),
                "url": f"https://store.example.com/product/{record['ProductCode']}"
            }
            products.append(product)
        
        # Return max 10 products
        return products[:10]
    
    except Exception as e:
        print(f"❌ ERROR in catalog_search: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return [{"error": str(e)}]


@mcp.tool()
def get_product_details(product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific product.
    
    Args:
        product_id: Salesforce Product2 Id
    
    Returns:
        Product details dictionary
    """
    if not SALESFORCE_AVAILABLE:
        return {"error": "Salesforce connection not available"}
    
    try:
        query = f"""
        SELECT Id, Name, ProductCode, Description, Family, Color__c, Size__c, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE Id = '{product_id}'
        """
        result = sf.query(query)
        
        if not result['records']:
            return {"error": "Product not found"}
        
        record = result['records'][0]
        price = None
        pricebook_entry_id = None
        
        if record.get('PricebookEntries') and record['PricebookEntries']['records']:
            price = record['PricebookEntries']['records'][0]['UnitPrice']
            pricebook_entry_id = record['PricebookEntries']['records'][0]['Id']
        
        return {
            "id": record['Id'],
            "name": record['Name'],
            "sku": record['ProductCode'],
            "description": record.get('Description', ''),
            "family": record.get('Family', ''),
            "color": record.get('Color__c', ''),
            "size": record.get('Size__c', ''),
            "price": price,
            "pricebook_entry_id": pricebook_entry_id,
            "image_url": record.get('Image_URL__c', ''),
            "in_stock": True
        }
    
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_product_by_name(product_name: str) -> Dict[str, Any]:
    """
    Get product details by exact product name.
    
    Args:
        product_name: Exact product name
    
    Returns:
        Product details dictionary
    """
    if not SALESFORCE_AVAILABLE:
        return {"error": "Salesforce connection not available"}
    
    try:
        escaped_name = product_name.replace("'", "\\'")
        
        query = f"""
        SELECT Id, Name, ProductCode, Description, Family, Color__c, Size__c, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE Name = '{escaped_name}' AND IsActive = true
        LIMIT 1
        """
        result = sf.query(query)
        
        if not result['records']:
            return {"error": "Product not found", "success": False}
        
        record = result['records'][0]
        price = None
        pricebook_entry_id = None
        
        if record.get('PricebookEntries') and record['PricebookEntries']['records']:
            price = record['PricebookEntries']['records'][0]['UnitPrice']
            pricebook_entry_id = record['PricebookEntries']['records'][0]['Id']
        
        return {
            "success": True,
            "id": record['Id'],
            "name": record['Name'],
            "sku": record['ProductCode'],
            "description": record.get('Description', ''),
            "family": record.get('Family', ''),
            "color": record.get('Color__c', ''),
            "size": record.get('Size__c', ''),
            "price": price,
            "pricebook_entry_id": pricebook_entry_id,
            "image_url": record.get('Image_URL__c', '')
        }
    
    except Exception as e:
        return {"error": str(e), "success": False}


@mcp.tool()
def create_customer_order(
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    items: List[Dict[str, Any]],
    shipping_address: Optional[str] = None,
    checkout_source: str = "WhatsApp Bot"
) -> Dict[str, Any]:
    """
    Create a new order in Salesforce CRM.
    
    Args:
        customer_name: Customer's full name
        customer_email: Customer's email
        customer_phone: Customer's phone number
        items: List of items with pricebook_entry_id, quantity, unit_price
        shipping_address: Shipping address (optional)
        checkout_source: Source of checkout
    
    Returns:
        Order details including order number and total
    """
    if not SALESFORCE_AVAILABLE:
        return {"error": "Salesforce connection not available", "success": False}
    
    try:
        # Step 1: Upsert Account
        account_id = upsert_account(
            email=customer_email,
            name=customer_name,
            phone=customer_phone
        )
        
        # Step 2: Get pricebook
        pricebook_id = get_standard_pricebook()
        
        # Step 3: Create Order
        order_data = Order(
            AccountId=account_id,
            Pricebook2Id=pricebook_id,
            EffectiveDate=datetime.now().strftime("%Y-%m-%d"),
            Status="Draft",
            CheckoutSource__c=checkout_source,
            StorefrontCartId__c=""
        )
        
        order_result = create_order(order_data)
        if not order_result or 'id' not in order_result:
            return {"error": "Failed to create order", "success": False}
        
        order_id = order_result['id']
        
        # Step 4: Create OrderItems
        total_amount = 0.0
        for item in items:
            order_item = OrderItem(
                OrderId=order_id,
                PricebookEntryId=item['pricebook_entry_id'],
                Quantity=item['quantity'],
                UnitPrice=item['unit_price']
            )
            create_order_item(order_item)
            total_amount += item['unit_price'] * item['quantity']
        
        # Step 5: Activate order
        sf.Order.update(order_id, {"Status": "Activated"})
        
        # Step 6: Get order number
        order_query = sf.query(f"SELECT OrderNumber FROM Order WHERE Id = '{order_id}'")
        order_number = order_query['records'][0]['OrderNumber']
        
        return {
            "success": True,
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount,
            "status": "Activated",
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    except Exception as e:
        return {"error": str(e), "success": False}


@mcp.tool()
def manage_cart(
    action: str,
    session_id: str,
    product_position: Optional[int] = None,
    product_id: Optional[str] = None,
    quantity: int = 1,
    last_search_results: Optional[List[Dict]] = None
) -> Dict[str, Any]:
    """
    Manage shopping cart operations with SMART product position handling.
    
    CRITICAL: last_search_results contains ONLY the 5 products shown to user.
    When user says "add option 3", they mean the 3rd item from those 5.
    
    Args:
        action: "add", "remove", "update", "view", "clear"
        session_id: User's session ID
        product_position: Position number (1-5) from displayed results
        product_id: Product ID for remove/update
        quantity: Quantity (default: 1)
        last_search_results: The 5 products user saw (NOT full search results)
    
    Returns:
        Cart state with success status
    """
    
    # In-memory cart storage
    if not hasattr(manage_cart, 'carts'):
        manage_cart.carts = {}
    
    carts = manage_cart.carts
    
    if session_id not in carts:
        carts[session_id] = []
    
    cart = carts[session_id]
    
    try:
        # ADD to cart
        if action == "add":
            if not last_search_results:
                return {
                    "success": False,
                    "error": "No search results available",
                    "message": "Please search for products first before adding to cart."
                }
            
            if not product_position:
                return {
                    "success": False,
                    "error": "Product position required",
                    "message": "Please specify which product (e.g., 'add option 3')"
                }
            
            # Validate position (1-5 for displayed items)
            if product_position < 1 or product_position > len(last_search_results):
                return {
                    "success": False,
                    "error": "Invalid position",
                    "message": f"Please choose a number between 1 and {len(last_search_results)}"
                }
            
            # Get product (convert 1-based to 0-based index)
            product = last_search_results[product_position - 1]
            
            # Check if already in cart
            existing_item = next((item for item in cart if item['product_id'] == product['id']), None)
            
            if existing_item:
                existing_item['quantity'] += quantity
                message = f"Updated {product['name']} quantity to {existing_item['quantity']}"
            else:
                cart.append({
                    "product_id": product['id'],
                    "name": product['name'],
                    "price": product['price'],
                    "pricebook_entry_id": product['pricebook_entry_id'],
                    "quantity": quantity,
                    "image_url": product.get('image_url', ''),
                    "color": product.get('color', ''),
                    "size": product.get('size', '')
                })
                message = f"Added {product['name']} to cart"
        
        # REMOVE from cart
        elif action == "remove":
            if not product_id:
                return {"success": False, "error": "Product ID required"}
            
            original_len = len(cart)
            cart[:] = [item for item in cart if item['product_id'] != product_id]
            
            if len(cart) == original_len:
                return {"success": False, "error": "Item not found in cart"}
            
            message = "Item removed from cart"
        
        # UPDATE quantity
        elif action == "update":
            if not product_id:
                return {"success": False, "error": "Product ID required"}
            
            item = next((item for item in cart if item['product_id'] == product_id), None)
            if item:
                item['quantity'] = quantity
                message = f"Updated quantity to {quantity}"
            else:
                return {"success": False, "error": "Item not found in cart"}
        
        # VIEW cart
        elif action == "view":
            message = "Cart retrieved"
        
        # CLEAR cart
        elif action == "clear":
            cart.clear()
            message = "Cart cleared"
        
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
        
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart)
        item_count = sum(item['quantity'] for item in cart)
        
        return {
            "success": True,
            "action": action,
            "message": message,
            "cart_items": cart,
            "item_count": item_count,
            "total": round(total, 2)
        }
    
    except Exception as e:
        print(f"❌ Error in manage_cart: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {"success": False, "error": str(e)}


@mcp.tool()
def lookup_order_status(
    order_number: Optional[str] = None,
    customer_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Look up order status by order number or customer email.
    
    Args:
        order_number: Order number to look up
        customer_email: Customer email (returns recent orders)
    
    Returns:
        Order status and details
    """
    if not SALESFORCE_AVAILABLE:
        return {"success": False, "error": "Salesforce connection not available"}
    
    try:
        if order_number:
            result = get_order_status(order_number)
            
            if not result or not result.get('records'):
                return {
                    "success": False,
                    "error": "Order not found",
                    "message": f"No order found with number {order_number}"
                }
            
            order = result['records'][0]
            
            # Get order items
            items = []
            if order.get('OrderItems') and order['OrderItems'].get('records'):
                for item in order['OrderItems']['records']:
                    items.append({
                        "product_name": item['Product2']['Name'],
                        "quantity": item['Quantity'],
                        "unit_price": item['UnitPrice'],
                        "subtotal": item['Quantity'] * item['UnitPrice']
                    })
            
            return {
                "success": True,
                "order_number": order.get('OrderNumber'),
                "status": order.get('Status'),
                "order_date": order.get('EffectiveDate'),
                "total_amount": order.get('TotalAmount', 0.0),
                "customer_name": order['Account']['Name'] if order.get('Account') else 'N/A',
                "items": items
            }
            
        elif customer_email:
            # Find account
            account_query = f"""
            SELECT Id, Name 
            FROM Account 
            WHERE PersonEmail = '{customer_email}' OR 
                  (IsPersonAccount = false AND BillingEmail = '{customer_email}')
            LIMIT 1
            """
            
            account_result = sf.query(account_query)
            
            if not account_result.get('records'):
                return {
                    "success": False,
                    "error": "No account found",
                    "message": f"No account found with email {customer_email}"
                }
            
            account_id = account_result['records'][0]['Id']
            account_name = account_result['records'][0]['Name']
            
            # Query orders
            order_query = f"""
            SELECT Id, OrderNumber, Status, EffectiveDate, TotalAmount,
                   (SELECT Product2.Name, Quantity, UnitPrice FROM OrderItems)
            FROM Order
            WHERE AccountId = '{account_id}'
            ORDER BY EffectiveDate DESC
            LIMIT 5
            """
            
            result = sf.query(order_query)
            
            if not result.get('records'):
                return {
                    "success": False,
                    "error": "No orders found",
                    "message": f"No orders found for {account_name}"
                }
            
            # Return most recent order
            order = result['records'][0]
            
            items = []
            if order.get('OrderItems') and order['OrderItems'].get('records'):
                for item in order['OrderItems']['records']:
                    items.append({
                        "product_name": item['Product2']['Name'],
                        "quantity": item['Quantity'],
                        "unit_price": item['UnitPrice'],
                        "subtotal": item['Quantity'] * item['UnitPrice']
                    })
            
            return {
                "success": True,
                "order_number": order.get('OrderNumber'),
                "status": order.get('Status'),
                "order_date": order.get('EffectiveDate'),
                "total_amount": order.get('TotalAmount', 0.0),
                "customer_name": account_name,
                "customer_email": customer_email,
                "items": items,
                "total_orders_found": len(result['records'])
            }
        
        else:
            return {
                "success": False,
                "error": "Missing parameters",
                "message": "Either order_number or customer_email is required"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Unable to retrieve order status: {str(e)}"
        }


# Run the server
if __name__ == "__main__":
    print("🚀 Starting Shopping Assistant MCP Server", file=sys.stderr)
    print(f"🌐 Host: {SERVER_HOST}", file=sys.stderr)
    print(f"🔌 Port: {SERVER_PORT}", file=sys.stderr)
    print(f"✅ Server running at http://{SERVER_HOST}:{SERVER_PORT}", file=sys.stderr)
    print(f"✅ SSE endpoint: http://{SERVER_HOST}:{SERVER_PORT}/sse", file=sys.stderr)
    
    mcp.run(transport="sse")