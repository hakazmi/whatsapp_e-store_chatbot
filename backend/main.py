"""
Enhanced FastAPI Backend with Session-Based Cart Synchronization
ADMIN PANEL: Shows only products created in current session
CUSTOMER MODE: Shows all products (unchanged)
"""
from fastapi import FastAPI, HTTPException, status, Query, Cookie, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
import os
import sys
import uuid
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, unquote

# Add salesforce folder to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from salesforce.client import sf

load_dotenv()

app = FastAPI(
    title="🛍️ E-Commerce Platform API with Cart Sync",
    description="Complete platform with WhatsApp and Web cart synchronization",
    version="3.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# IN-MEMORY SESSION STORAGE (Use Redis in production)
# ============================================================================
# Structure: {session_id: {"cart": [...], "phone": "...", "created_at": "..."}}
active_sessions: Dict[str, Dict] = {}

# Phone to Session mapping for WhatsApp users
phone_to_session: Dict[str, str] = {}

# 🆕 ADMIN SESSION STORAGE - Track products created in current session
admin_created_products: List[str] = []  # List of Product IDs created by admin

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ProductBase(BaseModel):
    Name: str = Field(..., min_length=3, max_length=120)
    ProductCode: str = Field(..., min_length=2, max_length=60)
    Price__c: float = Field(..., ge=0)
    Family: str
    Description: Optional[str] = Field(None, max_length=5000)
    Color__c: Optional[str] = Field(None, max_length=50)
    Size__c: Optional[str] = Field(None, max_length=50)
    Image_URL__c: Optional[str] = None
    IsActive: bool = Field(True)
    
    @field_validator('Price__c')
    @classmethod
    def validate_price(cls, v):
        return round(v, 2)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    Name: Optional[str] = Field(None, min_length=3, max_length=120)
    Price__c: Optional[float] = Field(None, ge=0)
    Family: Optional[str] = None
    Description: Optional[str] = Field(None, max_length=5000)
    Color__c: Optional[str] = Field(None, max_length=50)
    Size__c: Optional[str] = Field(None, max_length=50)
    Image_URL__c: Optional[str] = None
    IsActive: Optional[bool] = None
    
    @field_validator('Price__c')
    @classmethod
    def validate_price(cls, v):
        return round(v, 2) if v is not None else v


class ProductResponse(BaseModel):
    Id: str
    Name: str
    ProductCode: str
    Price__c: Optional[float]
    Family: Optional[str]
    Description: Optional[str]
    Color__c: Optional[str]
    Size__c: Optional[str]
    Image_URL__c: Optional[str]
    IsActive: bool
    CreatedDate: Optional[str]
    LastModifiedDate: Optional[str]


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    page: int
    page_size: int
    total: int


class CustomerProductResponse(BaseModel):
    id: str
    name: str
    price: float
    description: str
    color: str
    size: str
    product_code: str
    category: str
    image_url: str
    pricebook_entry_id: str


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)
    pricebook_entry_id: str
    price: float
    name: str
    color: Optional[str] = ""
    size: Optional[str] = ""
    image_url: Optional[str] = ""


class CustomerInfo(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    phone: Optional[str] = Field(None, max_length=20)


class OrderRequest(BaseModel):
    customer: CustomerInfo
    items: List[Dict[str, Any]]
    checkout_source: str = Field(default="Web")


class WhatsAppSessionRequest(BaseModel):
    phone: str
    session_id: Optional[str] = None

class DeleteConfirmation(BaseModel):
    sku_confirmation: str = Field(..., description="Type the SKU to confirm deletion")

class SearchFilters(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    color: Optional[str] = None
    size: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_standard_pricebook():
    """Get standard pricebook ID"""
    result = sf.query("SELECT Id FROM Pricebook2 WHERE IsStandard = true LIMIT 1")
    if result['records']:
        return result['records'][0]['Id']
    raise HTTPException(status_code=500, detail="Standard pricebook not found")

def check_sku_exists(sku: str, exclude_id: Optional[str] = None) -> bool:
    """Check if SKU already exists"""
    query = f"SELECT Id FROM Product2 WHERE ProductCode = '{sku}'"
    if exclude_id:
        query += f" AND Id != '{exclude_id}'"
    result = sf.query(query)
    return len(result['records']) > 0


def upsert_account(name: str, email: str, phone: str = "") -> str:
    """Create or update customer account"""
    query = f"SELECT Id FROM Account WHERE PersonEmail = '{email}' LIMIT 1"
    result = sf.query(query)
    
    if result['records']:
        account_id = result['records'][0]['Id']
        sf.Account.update(account_id, {'Name': name, 'Phone': phone})
        return account_id
    else:
        account_data = {'Name': name, 'PersonEmail': email, 'Phone': phone}
        result = sf.Account.create(account_data)
        return result['id']


def create_salesforce_order(account_id: str, items: List[Dict], checkout_source: str = "Web"):
    """Create order in Salesforce"""
    try:
        pricebook_id = get_standard_pricebook()
        total_amount = sum(item['unit_price'] * item['quantity'] for item in items)
        
        order_data = {
            'AccountId': account_id,
            'EffectiveDate': datetime.now().strftime('%Y-%m-%d'),
            'Status': 'Draft',
            'Pricebook2Id': pricebook_id,
            'Description': f'Order placed via {checkout_source}'
        }
        order_result = sf.Order.create(order_data)
        order_id = order_result['id']
        
        order_query = sf.query(f"SELECT OrderNumber FROM Order WHERE Id = '{order_id}'")
        order_number = order_query['records'][0]['OrderNumber']
        
        for item in items:
            order_item_data = {
                'OrderId': order_id,
                'Product2Id': item['product_id'],
                'PricebookEntryId': item['pricebook_entry_id'],
                'Quantity': item['quantity'],
                'UnitPrice': item['unit_price']
            }
            sf.OrderItem.create(order_item_data)
        
        sf.Order.update(order_id, {'Status': 'Activated'})
        
        return {
            "success": True,
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_or_create_session(session_id: Optional[str] = None, phone: Optional[str] = None) -> str:
    """Get existing session or create new one"""
    # If phone provided, check if session exists
    if phone and phone in phone_to_session:
        return phone_to_session[phone]
    
    # If session_id provided and exists
    if session_id and session_id in active_sessions:
        return session_id
    
    # Create new session
    new_session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
    active_sessions[new_session_id] = {
        "cart": [],
        "phone": phone or "",
        "created_at": datetime.now().isoformat()
    }
    
    if phone:
        phone_to_session[phone] = new_session_id
    
    print(f"✅ Created new session: {new_session_id} (phone: {phone})")
    return new_session_id

def clean_image_url(url: str) -> str:
    """
    Extract the real image link from a Google redirect URL or other formats.
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # Handle Google Images redirect URLs
    if "google.com/imgres" in url or "google" in url.lower():
        try:
            query = parse_qs(urlparse(url).query)
            if "imgurl" in query:
                return unquote(query["imgurl"][0])
            elif "url" in query:
                return unquote(query["url"][0])
        except Exception as e:
            print(f"⚠️ Failed to parse Google URL: {e}", file=sys.stderr)
    
    # Handle URL-encoded URLs
    if "%3A" in url or "%2F" in url:
        try:
            return unquote(url)
        except Exception as e:
            print(f"⚠️ Failed to decode URL: {e}", file=sys.stderr)
    
    return url


def validate_image_url(url: str) -> bool:
    """Validate if URL is a proper image URL."""
    if not url:
        return True
    
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    url_lower = url.lower()
    
    has_extension = any(ext in url_lower for ext in valid_extensions)
    
    if not has_extension:
        print(f"⚠️ URL may not be an image: {url}", file=sys.stderr)
    
    return True

# ============================================================================
# 🏠 GENERAL ENDPOINTS
# ============================================================================

@app.get("/", tags=["🏠 General"])
async def root():
    """API Information and available endpoints"""
    return {
        "name": "E-Commerce Platform API",
        "version": "3.0.0",
        "status": "✅ Online",
        "admin_session_products": len(admin_created_products),
        "features": {
            "customer": "Browse ALL products (including admin-created)",
            "admin": "View ONLY session-created products + Full CRUD"
        },
        "endpoints": {
            "customer": {
                "products": "GET /api/products",
                "search": "POST /api/products/search",
                "product_detail": "GET /api/products/{id}",
                "categories": "GET /api/categories",
                "add_to_cart": "POST /api/cart/{session_id}/add",
                "view_cart": "GET /api/cart/{session_id}",
                "place_order": "POST /api/orders",
                "track_order": "GET /api/orders/customer/{email}"
            },
            "admin": {
                "list_products": "GET /api/admin/products (session-filtered)",
                "create_product": "POST /api/admin/products",
                "get_product": "GET /api/admin/products/{id}",
                "update_product": "PATCH /api/admin/products/{id}",
                "delete_product": "DELETE /api/admin/products/{id}",
                "reset_session": "POST /api/admin/reset-session",
                "categories": "GET /api/admin/categories"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health", tags=["🏠 General"])
async def health_check():
    """Health check with Salesforce connection status"""
    try:
        sf.query("SELECT Id FROM Product2 LIMIT 1")
        return {
            "status": "🟢 Healthy",
            "salesforce": "✅ Connected",
            "admin_session_products": len(admin_created_products),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "🔴 Unhealthy",
            "salesforce": f"❌ Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# 🛒 CUSTOMER SHOPPING ENDPOINTS (SHOWS ALL PRODUCTS)
# ============================================================================

@app.get("/api/products", response_model=List[CustomerProductResponse], tags=["🛒 Shopping"])
async def get_all_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(200, ge=1, le=500, description="Maximum number of products")
):
    """Get ALL active products for customer browsing (UNCHANGED)"""
    try:
        query = """
        SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE IsActive = true
        """
        
        if category:
            query += f" AND Family = '{category}'"
        
        query += f" ORDER BY LastModifiedDate DESC LIMIT {limit}"
        
        results = sf.query(query)
        products = []
        
        for record in results['records']:
            pbe = record.get('PricebookEntries', {}).get('records', [])
            if pbe:
                products.append(CustomerProductResponse(
                    id=record['Id'],
                    name=record['Name'],
                    price=pbe[0]['UnitPrice'],
                    description=record.get('Description', ''),
                    color=record.get('Color__c', ''),
                    size=record.get('Size__c', ''),
                    product_code=record.get('ProductCode', ''),
                    category=record.get('Family', ''),
                    image_url=record.get('Image_URL__c', ''),
                    pricebook_entry_id=pbe[0]['Id']
                ))
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

@app.post("/api/products/search", response_model=List[CustomerProductResponse], tags=["🛒 Shopping"])
async def search_products(filters: SearchFilters):
    """Search ALL products with advanced filters (UNCHANGED)"""
    try:
        query = """
        SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE IsActive = true
        """
        
        conditions = []
        
        if filters.query:
            search_term = filters.query.replace("'", "\\'")
            conditions.append(f"(Name LIKE '%{search_term}%' OR Description LIKE '%{search_term}%')")
        
        if filters.category:
            conditions.append(f"Family = '{filters.category}'")
        
        if filters.color:
            conditions.append(f"Color__c = '{filters.color}'")
        
        if filters.size:
            conditions.append(f"Size__c = '{filters.size}'")
        
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY Name ASC LIMIT 500"
        
        results = sf.query(query)
        products = []
        
        for record in results['records']:
            pbe = record.get('PricebookEntries', {}).get('records', [])
            if pbe:
                price = pbe[0]['UnitPrice']
                
                if filters.price_min is not None and price < filters.price_min:
                    continue
                if filters.price_max is not None and price > filters.price_max:
                    continue
                
                products.append(CustomerProductResponse(
                    id=record['Id'],
                    name=record['Name'],
                    price=price,
                    description=record.get('Description', ''),
                    color=record.get('Color__c', ''),
                    size=record.get('Size__c', ''),
                    product_code=record.get('ProductCode', ''),
                    category=record.get('Family', ''),
                    image_url=record.get('Image_URL__c', ''),
                    pricebook_entry_id=pbe[0]['Id']
                ))
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/products/{product_id}", response_model=CustomerProductResponse, tags=["🛒 Shopping"])
async def get_product_detail(product_id: str):
    """Get detailed information about a single product (UNCHANGED)"""
    try:
        query = f"""
        SELECT Id, Name, ProductCode, Description, Color__c, Size__c, Family, Image_URL__c,
               (SELECT Id, UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE Id = '{product_id}' AND IsActive = true
        LIMIT 1
        """
        
        result = sf.query(query)
        if not result['records']:
            raise HTTPException(status_code=404, detail="Product not found")
        
        record = result['records'][0]
        pbe = record.get('PricebookEntries', {}).get('records', [])
        
        if not pbe:
            raise HTTPException(status_code=404, detail="Product price not available")
        
        return CustomerProductResponse(
            id=record['Id'],
            name=record['Name'],
            price=pbe[0]['UnitPrice'],
            description=record.get('Description', ''),
            color=record.get('Color__c', ''),
            size=record.get('Size__c', ''),
            product_code=record.get('ProductCode', ''),
            category=record.get('Family', ''),
            image_url=record.get('Image_URL__c', ''),
            pricebook_entry_id=pbe[0]['Id']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

@app.get("/api/categories", tags=["🛒 Shopping"])
async def get_categories():
    """Get all available product categories (UNCHANGED)"""
    try:
        query = """
        SELECT Family FROM Product2 
        WHERE IsActive = true AND Family != null 
        GROUP BY Family 
        ORDER BY Family
        """
        results = sf.query(query)
        categories = [record['Family'] for record in results['records']]
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

# ============================================================================
# 🛒 SHOPPING CART ENDPOINTS (UNCHANGED)
# ============================================================================

@app.get("/api/cart/session", tags=["🛒 Shopping"])
async def get_or_create_cart_session(
    response: Response,
    session_id: Optional[str] = Cookie(None),
    phone: Optional[str] = Query(None)
):
    """Get or create cart session"""
    session = get_or_create_session(session_id, phone)
    
    response.set_cookie(
        key="session_id",
        value=session,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    
    cart = active_sessions[session]["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart)
    
    return {
        "session_id": session,
        "cart": cart,
        "total": round(total, 2),
        "item_count": sum(item["quantity"] for item in cart)
    }


@app.post("/api/cart/{session_id}/add", tags=["🛒 Shopping"])
async def add_to_cart(session_id: str, item: CartItemRequest):
    """Add item to cart"""
    if session_id not in active_sessions:
        get_or_create_session(session_id)
    
    cart = active_sessions[session_id]["cart"]
    
    existing_item = next((ci for ci in cart if ci["product_id"] == item.product_id), None)
    
    if existing_item:
        existing_item["quantity"] += item.quantity
        message = f"Updated {item.name} quantity"
    else:
        cart.append({
            "product_id": item.product_id,
            "name": item.name,
            "price": item.price,
            "pricebook_entry_id": item.pricebook_entry_id,
            "quantity": item.quantity,
            "image_url": item.image_url,
            "color": item.color,
            "size": item.size
        })
        message = f"Added {item.name} to cart"
    
    total = sum(ci["price"] * ci["quantity"] for ci in cart)
    
    print(f"📦 Cart updated for session {session_id}: {len(cart)} items")
    
    return {
        "success": True,
        "message": message,
        "cart": cart,
        "total": round(total, 2),
        "item_count": sum(ci["quantity"] for ci in cart)
    }


@app.get("/api/cart/{session_id}", tags=["🛒 Shopping"])
async def get_cart(session_id: str):
    """Get cart contents"""
    if session_id not in active_sessions:
        return {"cart": [], "total": 0, "item_count": 0}
    
    cart = active_sessions[session_id]["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart)
    
    return {
        "cart": cart,
        "total": round(total, 2),
        "item_count": sum(item["quantity"] for item in cart)
    }


@app.put("/api/cart/{session_id}/item/{product_id}", tags=["🛒 Shopping"])
async def update_cart_quantity(session_id: str, product_id: str, quantity: int):
    """Update item quantity"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = active_sessions[session_id]["cart"]
    
    if quantity <= 0:
        active_sessions[session_id]["cart"] = [
            item for item in cart if item["product_id"] != product_id
        ]
        message = "Item removed"
    else:
        item = next((ci for ci in cart if ci["product_id"] == product_id), None)
        if item:
            item["quantity"] = quantity
            message = "Cart updated"
        else:
            raise HTTPException(status_code=404, detail="Item not in cart")
    
    cart = active_sessions[session_id]["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart)
    
    return {
        "success": True,
        "message": message,
        "cart": cart,
        "total": round(total, 2)
    }


@app.delete("/api/cart/{session_id}/item/{product_id}", tags=["🛒 Shopping"])
async def remove_from_cart(session_id: str, product_id: str):
    """Remove item from cart"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart = active_sessions[session_id]["cart"]
    active_sessions[session_id]["cart"] = [
        item for item in cart if item["product_id"] != product_id
    ]
    
    return {"success": True, "message": "Item removed"}


@app.delete("/api/cart/{session_id}", tags=["🛒 Shopping"])
async def clear_cart(session_id: str):
    """Clear cart"""
    if session_id in active_sessions:
        active_sessions[session_id]["cart"] = []
        print(f"🧹 Cart cleared for session {session_id}")
    return {"success": True, "message": "Cart cleared"}


# ============================================================================
# 📲 WHATSAPP SESSION ENDPOINTS (UNCHANGED)
# ============================================================================

pending_sessions: Dict[str, Dict] = {}

@app.post("/api/whatsapp/prepare-session", tags=["📱 WhatsApp"])
async def prepare_whatsapp_session(data: Dict[str, Any]):
    """Prepare session for WhatsApp linking"""
    session_id = data.get("session_id")
    timestamp = data.get("timestamp")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    pending_sessions[session_id] = {
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat()
    }
    
    print(f"📝 Prepared session for WhatsApp: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session prepared for WhatsApp linking"
    }


@app.get("/api/whatsapp/pending-sessions", tags=["📱 WhatsApp"])
async def get_pending_sessions():
    """Get all pending sessions waiting for WhatsApp link"""
    current_time = datetime.now()
    expired = []
    
    for session_id, data in pending_sessions.items():
        created = datetime.fromisoformat(data["created_at"])
        if (current_time - created).total_seconds() > 300:
            expired.append(session_id)
    
    for session_id in expired:
        del pending_sessions[session_id]
    
    return {
        "pending_sessions": list(pending_sessions.keys()),
        "count": len(pending_sessions)
    }

@app.delete("/api/whatsapp/pending-sessions/{session_id}", tags=["📱 WhatsApp"])
async def remove_pending_session(session_id: str):
    """Remove a pending session after it's been linked"""
    if session_id in pending_sessions:
        del pending_sessions[session_id]
        print(f"🗑️ Removed pending session: {session_id}")
        return {"success": True, "message": "Session removed from pending list"}
    
    return {"success": False, "message": "Session not found"}

@app.post("/api/whatsapp/link-session", tags=["📱 WhatsApp"])
async def link_whatsapp_session(data: WhatsAppSessionRequest):
    """Link WhatsApp phone number to existing session or create new"""
    session_id = get_or_create_session(data.session_id, data.phone)
    
    cart = active_sessions[session_id]["cart"]
    
    return {
        "success": True,
        "session_id": session_id,
        "phone": data.phone,
        "cart_items": len(cart),
        "message": "Session linked successfully"
    }


@app.get("/api/whatsapp/session/{phone}", tags=["📱 WhatsApp"])
async def get_whatsapp_session(phone: str):
    """Get session info by phone number"""
    if phone not in phone_to_session:
        raise HTTPException(status_code=404, detail="No session found for this phone")
    
    session_id = phone_to_session[phone]
    cart = active_sessions[session_id]["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart)
    
    return {
        "session_id": session_id,
        "phone": phone,
        "cart": cart,
        "total": round(total, 2),
        "item_count": sum(item["quantity"] for item in cart)
    }


# ============================================================================
# 📦 ORDER ENDPOINTS (UNCHANGED)
# ============================================================================

@app.post("/api/orders", tags=["📦 Orders"])
async def place_order(order_request: OrderRequest, session_id: Optional[str] = Query(None)):
    """Place order and clear cart"""
    try:
        if not order_request.items:
            raise HTTPException(status_code=400, detail="Order must contain items")
        
        account_id = upsert_account(
            name=order_request.customer.name,
            email=order_request.customer.email,
            phone=order_request.customer.phone or ""
        )
        
        result = create_salesforce_order(
            account_id=account_id,
            items=order_request.items,
            checkout_source=order_request.checkout_source
        )
        
        if result["success"]:
            if session_id and session_id in active_sessions:
                active_sessions[session_id]["cart"] = []
                print(f"🧹 Cart cleared after order for session {session_id}")
            
            return {
                "success": True,
                "order_number": result["order_number"],
                "order_id": result["order_id"],
                "total_amount": round(result["total_amount"], 2),
                "message": "Order placed successfully"
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")


@app.get("/api/orders/customer/{email}", tags=["📦 Orders"])
async def get_customer_orders(email: str):
    """Get customer orders"""
    try:
        account_query = f"SELECT Id FROM Account WHERE PersonEmail = '{email}' LIMIT 1"
        account_result = sf.query(account_query)
        
        if not account_result['records']:
            return {"orders": [], "message": "No orders found"}
        
        account_id = account_result['records'][0]['Id']
        
        orders_query = f"""
        SELECT Id, OrderNumber, Status, TotalAmount, EffectiveDate, CreatedDate,
               (SELECT Product2.Name, Quantity, UnitPrice FROM OrderItems)
        FROM Order
        WHERE AccountId = '{account_id}'
        ORDER BY CreatedDate DESC
        """
        
        orders_result = sf.query(orders_query)
        
        orders = []
        for order in orders_result['records']:
            items = []
            if order.get('OrderItems') and order['OrderItems'].get('records'):
                for item in order['OrderItems']['records']:
                    items.append({
                        "product_name": item['Product2']['Name'],
                        "quantity": item['Quantity'],
                        "unit_price": item['UnitPrice']
                    })
            
            orders.append({
                "order_id": order['Id'],
                "order_number": order['OrderNumber'],
                "status": order['Status'],
                "total_amount": order.get('TotalAmount', 0),
                "order_date": order['EffectiveDate'],
                "created_date": order['CreatedDate'],
                "items": items
            })
        
        return {"orders": orders, "count": len(orders)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 🔧 ADMIN - PRODUCT CRUD ENDPOINTS (SESSION-FILTERED)
# ============================================================================

@app.get("/api/admin/products", response_model=ProductListResponse, tags=["🔧 Admin - Products"])
async def admin_list_products(
    q: Optional[str] = Query(None, description="🔍 Search by title or SKU"),
    category: Optional[str] = Query(None, description="🎯 Filter by category"),
    status: Optional[Literal["active", "inactive"]] = Query(None, description="✅ Filter by status"),
    sort: Optional[Literal["updated", "price", "name"]] = Query("updated", description="📊 Sort field"),
    order: Optional[Literal["asc", "desc"]] = Query("desc", description="🔼 Sort order"),
    page: int = Query(1, ge=1, description="📄 Page number"),
    page_size: int = Query(20, ge=1, le=100, description="📏 Items per page"),
):
    """📋 Admin: List ONLY products created in current session"""
    
    try:
        # 🆕 FILTER: Only show products created in this session
        if not admin_created_products:
            # No products created yet
            return ProductListResponse(
                items=[],
                page=page,
                page_size=page_size,
                total=0
            )
        
        # Build ID filter for session products
        product_ids = "', '".join(admin_created_products)
        
        # 🔧 FIXED: Remove WHERE 1=1 (invalid SOQL)
        soql = f"""
        SELECT Id, Name, ProductCode, Description, Family, Color__c, Size__c, 
               Image_URL__c, IsActive, CreatedDate, LastModifiedDate,
               (SELECT UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2
        WHERE Id IN ('{product_ids}')
        """
        
        conditions = []
        if q:
            search_term = q.replace("'", "\\'")
            conditions.append(f"(Name LIKE '%{search_term}%' OR ProductCode LIKE '%{search_term}%')")
        if category:
            conditions.append(f"Family = '{category}'")
        if status:
            is_active = "true" if status == "active" else "false"
            conditions.append(f"IsActive = {is_active}")
        
        if conditions:
            soql += " AND " + " AND ".join(conditions)
        
        sort_field_map = {"updated": "LastModifiedDate", "price": "Name", "name": "Name"}
        sort_field = sort_field_map.get(sort, "LastModifiedDate")
        sort_order = order.upper()
        soql += f" ORDER BY {sort_field} {sort_order}"
        
        print(f"🔍 Executing SOQL query:", file=sys.stderr)
        print(f"   Filtering {len(admin_created_products)} session products", file=sys.stderr)
        
        result = sf.query_all(soql)
        total_records = result['totalSize']
        
        print(f"✅ Found {total_records} session products", file=sys.stderr)
        
        products = []
        for record in result['records']:
            try:
                price = None
                if record.get('PricebookEntries') and record['PricebookEntries'].get('records'):
                    price = record['PricebookEntries']['records'][0].get('UnitPrice')
                
                product = ProductResponse(
                    Id=record['Id'],
                    Name=record['Name'],
                    ProductCode=record['ProductCode'],
                    Price__c=price,
                    Family=record.get('Family'),
                    Description=record.get('Description'),
                    Color__c=record.get('Color__c'),
                    Size__c=record.get('Size__c'),
                    Image_URL__c=record.get('Image_URL__c'),
                    IsActive=record.get('IsActive', False),
                    CreatedDate=record.get('CreatedDate'),
                    LastModifiedDate=record.get('LastModifiedDate')
                )
                products.append(product)
            except Exception as e:
                print(f"⚠️ Failed to parse product {record.get('Id', 'unknown')}: {e}", file=sys.stderr)
                continue
        
        print(f"✅ Successfully parsed {len(products)} products", file=sys.stderr)
        
        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_products = products[start_idx:end_idx]
        
        return ProductListResponse(
            items=paginated_products,
            page=page,
            page_size=page_size,
            total=total_records
        )
    
    except Exception as e:
        print(f"❌ Admin products list error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch products: {str(e)}"
        )

@app.get("/api/admin/products/{product_id}", response_model=ProductResponse, tags=["🔧 Admin - Products"])
async def admin_get_product(product_id: str):
    """🔍 Admin: Get single product by ID"""
    try:
        soql = f"""
        SELECT Id, Name, ProductCode, Description, Family, Color__c, Size__c, 
               Image_URL__c, IsActive, CreatedDate, LastModifiedDate,
               (SELECT UnitPrice FROM PricebookEntries WHERE IsActive = true LIMIT 1)
        FROM Product2 WHERE Id = '{product_id}'
        """
        result = sf.query(soql)
        if not result['records']:
            raise HTTPException(status_code=404, detail="Product not found")
        
        record = result['records'][0]
        price = None
        if record.get('PricebookEntries') and record['PricebookEntries']['records']:
            price = record['PricebookEntries']['records'][0].get('UnitPrice')
        
        return ProductResponse(
            Id=record['Id'], Name=record['Name'], ProductCode=record['ProductCode'],
            Price__c=price, Family=record.get('Family'), Description=record.get('Description'),
            Color__c=record.get('Color__c'), Size__c=record.get('Size__c'),
            Image_URL__c=record.get('Image_URL__c'), IsActive=record.get('IsActive', False),
            CreatedDate=record.get('CreatedDate'), LastModifiedDate=record.get('LastModifiedDate')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

@app.post("/api/admin/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["🔧 Admin - Products"])
async def admin_create_product(product: ProductCreate):
    """➕ Admin: Create new product (ADDS TO SESSION LIST)"""
    
    if check_sku_exists(product.ProductCode):
        raise HTTPException(status_code=409, detail=f"SKU '{product.ProductCode}' already exists")
    
    try:
        # Clean image URL
        cleaned_image_url = ""
        if product.Image_URL__c:
            original_url = product.Image_URL__c
            cleaned_image_url = clean_image_url(original_url)
            
            print(f"🖼️ Image URL cleaning:", file=sys.stderr)
            print(f"   Original: {original_url[:100]}...", file=sys.stderr)
            print(f"   Cleaned:  {cleaned_image_url[:100]}...", file=sys.stderr)
            
            validate_image_url(cleaned_image_url)
        
        product_data = {
            "Name": product.Name,
            "ProductCode": product.ProductCode,
            "Family": product.Family,
            "Description": product.Description,
            "Color__c": product.Color__c,
            "Size__c": product.Size__c,
            "Image_URL__c": cleaned_image_url,
            "IsActive": product.IsActive
        }
        
        result = sf.Product2.create(product_data)
        product_id = result['id']
        
        # 🆕 ADD TO SESSION LIST
        admin_created_products.append(product_id)
        
        print(f"✅ Product created: {product.Name} (ID: {product_id})", file=sys.stderr)
        print(f"📊 Session products: {len(admin_created_products)}", file=sys.stderr)
        
        # Add to pricebook
        pricebook_id = get_standard_pricebook()
        sf.PricebookEntry.create({
            "Pricebook2Id": pricebook_id,
            "Product2Id": product_id,
            "UnitPrice": product.Price__c,
            "IsActive": True
        })
        
        # Return created product
        return await admin_get_product(product_id)
    
    except Exception as e:
        print(f"❌ Product creation error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

@app.patch("/api/admin/products/{product_id}", response_model=ProductResponse, tags=["🔧 Admin - Products"])
async def admin_update_product(product_id: str, product_update: ProductUpdate):
    """✏️ Admin: Update existing product"""
    
    # Verify product exists
    existing = sf.query(f"SELECT Id FROM Product2 WHERE Id = '{product_id}'")
    if not existing['records']:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        update_data = {}
        
        if product_update.Name is not None:
            update_data["Name"] = product_update.Name
        if product_update.Family is not None:
            update_data["Family"] = product_update.Family
        if product_update.Description is not None:
            update_data["Description"] = product_update.Description
        if product_update.Color__c is not None:
            update_data["Color__c"] = product_update.Color__c
        if product_update.Size__c is not None:
            update_data["Size__c"] = product_update.Size__c
        
        # Clean image URL if being updated
        if product_update.Image_URL__c is not None:
            original_url = product_update.Image_URL__c
            cleaned_image_url = clean_image_url(original_url)
            
            print(f"🖼️ Image URL cleaning (update):", file=sys.stderr)
            print(f"   Original: {original_url[:100]}...", file=sys.stderr)
            print(f"   Cleaned:  {cleaned_image_url[:100]}...", file=sys.stderr)
            
            update_data["Image_URL__c"] = cleaned_image_url
            validate_image_url(cleaned_image_url)
        
        if product_update.IsActive is not None:
            update_data["IsActive"] = product_update.IsActive
        
        # Update product fields
        if update_data:
            sf.Product2.update(product_id, update_data)
            print(f"✅ Product updated: {product_id}", file=sys.stderr)
        
        # Update price if provided
        if product_update.Price__c is not None:
            pricebook_result = sf.query(f"""
                SELECT Id FROM PricebookEntry 
                WHERE Product2Id = '{product_id}' AND IsActive = true LIMIT 1
            """)
            if pricebook_result['records']:
                entry_id = pricebook_result['records'][0]['Id']
                sf.PricebookEntry.update(entry_id, {"UnitPrice": product_update.Price__c})
                print(f"✅ Price updated: ${product_update.Price__c}", file=sys.stderr)
        
        return await admin_get_product(product_id)
    
    except Exception as e:
        print(f"❌ Product update error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")

@app.delete("/api/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["🔧 Admin - Products"])
async def admin_delete_product(product_id: str, confirmation: DeleteConfirmation):
    """🗑️ Admin: Soft delete product (requires SKU confirmation)"""
    result = sf.query(f"SELECT ProductCode FROM Product2 WHERE Id = '{product_id}'")
    if not result['records']:
        raise HTTPException(status_code=404, detail="Product not found")
    
    actual_sku = result['records'][0]['ProductCode']
    if confirmation.sku_confirmation != actual_sku:
        raise HTTPException(
            status_code=400,
            detail=f"❌ SKU confirmation does not match. Expected: '{actual_sku}'"
        )
    
    try:
        sf.Product2.update(product_id, {"IsActive": False})
        
        # 🆕 REMOVE FROM SESSION LIST
        if product_id in admin_created_products:
            admin_created_products.remove(product_id)
            print(f"📊 Session products: {len(admin_created_products)}", file=sys.stderr)
        
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")

@app.post("/api/admin/reset-session", tags=["🔧 Admin - Products"])
async def admin_reset_session():
    """🔄 Reset admin session (clear product list)"""
    global admin_created_products
    old_count = len(admin_created_products)
    admin_created_products = []
    
    print(f"🔄 Admin session reset: {old_count} products cleared", file=sys.stderr)
    
    return {
        "success": True,
        "message": f"Session reset. {old_count} products cleared from view.",
        "note": "Products still exist in Salesforce, just hidden from admin panel until re-run."
    }

@app.get("/api/admin/categories", tags=["🔍 Search & Filters"])
async def admin_get_categories():
    """🏷️ Admin: Get all product categories"""
    try:
        result = sf.query("""
            SELECT Family FROM Product2 WHERE Family != null 
            GROUP BY Family ORDER BY Family
        """)
        categories = [record['Family'] for record in result['records']]
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@app.get("/api/admin/stats", tags=["🔧 Admin - Products"])
async def admin_get_stats():
    """📊 Admin: Get dashboard statistics"""
    try:
        # Session products only
        session_products_count = len(admin_created_products)
        
        # All products (for comparison)
        total_query = sf.query("SELECT COUNT() FROM Product2")
        total_products = total_query['totalSize']
        
        active_query = sf.query("SELECT COUNT() FROM Product2 WHERE IsActive = true")
        active_products = active_query['totalSize']
        
        # Recent orders
        orders_query = sf.query("""
            SELECT COUNT() FROM Order 
            WHERE CreatedDate = LAST_N_DAYS:30
        """)
        recent_orders = orders_query['totalSize']
        
        return {
            "session": {
                "products_created": session_products_count,
                "message": "Products visible in admin panel this session"
            },
            "salesforce": {
                "total": total_products,
                "active": active_products,
                "inactive": total_products - active_products
            },
            "recent_orders": recent_orders,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")

# ============================================================================
# 🔍 SEARCH & FILTERS - SHARED ENDPOINTS
# ============================================================================

@app.get("/api/colors", tags=["🔍 Search & Filters"])
async def get_colors():
    """🎨 Get all available product colors"""
    try:
        result = sf.query("""
            SELECT Color__c FROM Product2 
            WHERE IsActive = true AND Color__c != null 
            GROUP BY Color__c 
            ORDER BY Color__c
        """)
        colors = [record['Color__c'] for record in result['records']]
        return {"colors": colors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch colors: {str(e)}")

@app.get("/api/sizes", tags=["🔍 Search & Filters"])
async def get_sizes():
    """📏 Get all available product sizes"""
    try:
        result = sf.query("""
            SELECT Size__c FROM Product2 
            WHERE IsActive = true AND Size__c != null 
            GROUP BY Size__c 
            ORDER BY Size__c
        """)
        sizes = [record['Size__c'] for record in result['records']]
        return {"sizes": sizes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sizes: {str(e)}")

@app.get("/api/price-range", tags=["🔍 Search & Filters"])
async def get_price_range():
    """💰 Get min and max price for filtering"""
    try:
        result = sf.query("""
            SELECT MIN(UnitPrice) minPrice, MAX(UnitPrice) maxPrice 
            FROM PricebookEntry 
            WHERE IsActive = true
        """)
        if result['records']:
            record = result['records'][0]
            return {
                "min": record.get('minPrice', 0),
                "max": record.get('maxPrice', 0)
            }
        return {"min": 0, "max": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price range: {str(e)}")

# ============================================================================
# 🚀 SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting E-Commerce Platform API...")
    print("🛒 Customer Shopping: http://localhost:8000/api/products (ALL products)")
    print("🔧 Admin Panel: http://localhost:8000/api/admin/products (SESSION products only)")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print("\n💡 Admin Feature: Only products created in THIS session appear in admin panel")
    print("   Customer mode: Shows ALL products including admin-created ones")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)