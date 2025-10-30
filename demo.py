import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust if your FastAPI runs on different port

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'current_view' not in st.session_state:
    st.session_state.current_view = "customer"
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

def call_api(endpoint, method="GET", data=None, params=None):
    """Helper function to call API endpoints"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PATCH":
            response = requests.patch(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def get_products(filters=None):
    """Get products from API"""
    params = {}
    if filters:
        if filters.get('category'):
            params['category'] = filters['category']
        if filters.get('limit'):
            params['limit'] = filters['limit']
    
    return call_api("/api/products", params=params)

def search_products(search_filters):
    """Search products with filters"""
    return call_api("/api/products/search", method="POST", data=search_filters)

def get_product_detail(product_id):
    """Get detailed product information"""
    return call_api(f"/api/products/{product_id}")

def get_categories():
    """Get all categories"""
    result = call_api("/api/categories")
    return result.get('categories', []) if result else []

def get_colors():
    """Get all colors"""
    result = call_api("/api/colors")
    return result.get('colors', []) if result else []

def get_sizes():
    """Get all sizes"""
    result = call_api("/api/sizes")
    return result.get('sizes', []) if result else []

def get_price_range():
    """Get price range"""
    return call_api("/api/price-range")

def add_to_cart(product_id, quantity=1):
    """Add item to cart"""
    data = {
        "product_id": product_id,
        "quantity": quantity
    }
    return call_api(f"/api/cart/{st.session_state.session_id}/add", method="POST", data=data)

def get_cart():
    """Get current cart"""
    return call_api(f"/api/cart/{st.session_state.session_id}")

def update_cart_item(product_id, quantity):
    """Update cart item quantity"""
    return call_api(f"/api/cart/{st.session_state.session_id}/item/{product_id}", method="PUT", params={"quantity": quantity})

def remove_from_cart(product_id):
    """Remove item from cart"""
    return call_api(f"/api/cart/{st.session_state.session_id}/item/{product_id}", method="DELETE")

def clear_cart():
    """Clear entire cart"""
    return call_api(f"/api/cart/{st.session_state.session_id}", method="DELETE")

def place_order(customer_info, items, checkout_source="Web"):
    """Place order"""
    data = {
        "customer": customer_info,
        "items": items,
        "checkout_source": checkout_source
    }
    return call_api("/api/orders", method="POST", data=data)

# Admin functions
def admin_get_products(filters=None):
    """Admin: Get products with filters"""
    params = filters or {}
    return call_api("/api/admin/products", params=params)

def admin_get_product(product_id):
    """Admin: Get single product"""
    return call_api(f"/api/admin/products/{product_id}")

def admin_create_product(product_data):
    """Admin: Create new product"""
    return call_api("/api/admin/products", method="POST", data=product_data)

def admin_update_product(product_id, product_data):
    """Admin: Update product"""
    return call_api(f"/api/admin/products/{product_id}", method="PATCH", data=product_data)

def admin_delete_product(product_id, sku):
    """Admin: Delete product"""
    params = {"sku_confirmation": sku}
    return call_api(f"/api/admin/products/{product_id}", method="DELETE", params=params)

def admin_get_categories():
    """Admin: Get categories"""
    result = call_api("/api/admin/categories")
    return result.get('categories', []) if result else []

def admin_get_stats():
    """Admin: Get dashboard stats"""
    return call_api("/api/admin/stats")

def display_product_card(product, show_add_to_cart=True):
    """Display product in a card format"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if product.get('image_url'):
            st.image(product['image_url'], width=100)
        else:
            st.image("https://via.placeholder.com/100x100?text=No+Image", width=100)
    
    with col2:
        st.subheader(product['name'])
        st.write(f"**${product['price']:.2f}**")
        
        if product.get('color'):
            st.write(f"Color: {product['color']}")
        if product.get('size'):
            st.write(f"Size: {product['size']}")
        if product.get('description'):
            st.write(product['description'][:100] + "..." if len(product.get('description', '')) > 100 else product.get('description', ''))
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if show_add_to_cart:
                if st.button("Add to Cart", key=f"add_{product['id']}"):
                    result = add_to_cart(product['id'], 1)
                    if result and result.get('success'):
                        st.success("Added to cart!")
                        st.rerun()
        
        with col_btn2:
            if st.button("View Details", key=f"view_{product['id']}"):
                st.session_state.selected_product = product['id']
                st.rerun()

def customer_home():
    """Customer shopping interface"""
    st.title("🛍️ E-Commerce Store")
    
    # Search and filters
    with st.expander("🔍 Search & Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("Search products")
            category_filter = st.selectbox("Category", [""] + get_categories())
        
        with col2:
            colors = get_colors()
            color_filter = st.selectbox("Color", [""] + colors)
            sizes = get_sizes()
            size_filter = st.selectbox("Size", [""] + sizes)
        
        with col3:
            price_range = get_price_range()
            if price_range:
                min_price, max_price = st.slider(
                    "Price Range",
                    min_value=float(price_range.get('min', 0)),
                    max_value=float(price_range.get('max', 1000)),
                    value=(float(price_range.get('min', 0)), float(price_range.get('max', 1000)))
                )
            else:
                min_price, max_price = 0, 1000
    
    # Apply filters
    filters = {}
    if search_query:
        filters['query'] = search_query
    if category_filter:
        filters['category'] = category_filter
    if color_filter:
        filters['color'] = color_filter
    if size_filter:
        filters['size'] = size_filter
    
    filters['price_min'] = min_price
    filters['price_max'] = max_price
    
    # Get and display products
    if filters.get('query') or filters.get('category') or filters.get('color') or filters.get('size'):
        products = search_products(filters)
    else:
        products = get_products({'limit': 20})
    
    if products:
        st.subheader(f"📦 Products ({len(products)} found)")
        
        # Display products in grid
        cols = st.columns(3)
        for idx, product in enumerate(products):
            with cols[idx % 3]:
                display_product_card(product)
    else:
        st.info("No products found. Try adjusting your filters.")

def product_detail_view():
    """Display detailed product view"""
    if st.session_state.selected_product:
        product = get_product_detail(st.session_state.selected_product)
        
        if product:
            st.button("← Back to Products", on_click=lambda: setattr(st.session_state, 'selected_product', None))
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if product.get('image_url'):
                    st.image(product['image_url'], use_column_width=True)
                else:
                    st.image("https://via.placeholder.com/300x300?text=No+Image", use_column_width=True)
            
            with col2:
                st.title(product['name'])
                st.write(f"**Price: ${product['price']:.2f}**")
                
                if product.get('color'):
                    st.write(f"**Color:** {product['color']}")
                if product.get('size'):
                    st.write(f"**Size:** {product['size']}")
                if product.get('category'):
                    st.write(f"**Category:** {product['category']}")
                if product.get('product_code'):
                    st.write(f"**SKU:** {product['product_code']}")
                
                st.write("---")
                st.write("**Description:**")
                st.write(product.get('description', 'No description available.'))
                
                # Add to cart section
                st.write("---")
                quantity = st.number_input("Quantity", min_value=1, value=1, key="detail_quantity")
                
                if st.button("Add to Cart", type="primary", use_container_width=True):
                    result = add_to_cart(product['id'], quantity)
                    if result and result.get('success'):
                        st.success(f"Added {quantity} item(s) to cart!")
        else:
            st.error("Product not found")
            st.session_state.selected_product = None

def shopping_cart():
    """Shopping cart view"""
    st.title("🛒 Shopping Cart")
    
    cart_data = get_cart()
    
    if not cart_data or not cart_data.get('cart'):
        st.info("Your cart is empty")
        return
    
    cart_items = cart_data['cart']
    total = cart_data.get('total', 0)
    item_count = cart_data.get('item_count', 0)
    
    st.write(f"**Total Items:** {item_count}")
    st.write(f"**Total Amount:** ${total:.2f}")
    
    for item in cart_items:
        product = item['product']
        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
        
        with col1:
            if product.get('image_url'):
                st.image(product['image_url'], width=50)
            else:
                st.image("https://via.placeholder.com/50x50?text=No+Image", width=50)
        
        with col2:
            st.write(f"**{product['name']}**")
            st.write(f"${product['price']:.2f} each")
        
        with col3:
            new_quantity = st.number_input(
                "Qty", 
                min_value=0, 
                value=item['quantity'],
                key=f"qty_{product['id']}"
            )
            
            if new_quantity != item['quantity']:
                if new_quantity == 0:
                    remove_from_cart(product['id'])
                    st.rerun()
                else:
                    update_cart_item(product['id'], new_quantity)
                    st.rerun()
        
        with col4:
            if st.button("🗑️", key=f"remove_{product['id']}"):
                remove_from_cart(product['id'])
                st.rerun()
    
    st.write("---")
    
    # Checkout section
    st.subheader("Checkout")
    
    with st.form("checkout_form"):
        st.write("**Customer Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Full Name", placeholder="John Doe")
            customer_email = st.text_input("Email", placeholder="john@example.com")
        
        with col2:
            customer_phone = st.text_input("Phone", placeholder="+1234567890")
            checkout_source = st.selectbox("Order Source", ["Web", "Mobile", "Voice"])
        
        if st.form_submit_button("Place Order", type="primary"):
            if not customer_name or not customer_email:
                st.error("Please fill in required fields: Name and Email")
            else:
                customer_info = {
                    "name": customer_name,
                    "email": customer_email,
                    "phone": customer_phone
                }
                
                # Prepare order items
                order_items = []
                for item in cart_items:
                    order_items.append({
                        "product_id": item['product']['id'],
                        "pricebook_entry_id": item['product']['pricebook_entry_id'],
                        "price": item['product']['price'],
                        "quantity": item['quantity']
                    })
                
                result = place_order(customer_info, order_items, checkout_source)
                
                if result and result.get('success'):
                    st.success(f"Order placed successfully! Order #: {result.get('order_number')}")
                    clear_cart()
                    st.rerun()
                else:
                    st.error("Failed to place order")

def admin_dashboard():
    """Admin panel dashboard"""
    st.title("🔧 Admin Panel")
    
    # Quick stats
    stats = admin_get_stats()
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", stats['products']['total'])
        with col2:
            st.metric("Active Products", stats['products']['active'])
        with col3:
            st.metric("Inactive Products", stats['products']['inactive'])
        with col4:
            st.metric("Recent Orders (30d)", stats['recent_orders'])
    
    st.write("---")
    
    # Product management
    st.subheader("Product Management")
    
    # Search and filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        admin_search = st.text_input("Search", key="admin_search")
    with col2:
        admin_category = st.selectbox("Category", [""] + admin_get_categories(), key="admin_category")
    with col3:
        admin_status = st.selectbox("Status", ["", "active", "inactive"], key="admin_status")
    with col4:
        admin_sort = st.selectbox("Sort By", ["updated", "name", "price"], key="admin_sort")
    
    # Get products with filters
    filters = {}
    if admin_search:
        filters['q'] = admin_search
    if admin_category:
        filters['category'] = admin_category
    if admin_status:
        filters['status'] = admin_status
    if admin_sort:
        filters['sort'] = admin_sort
    
    filters['page'] = 1
    filters['page_size'] = 20
    
    products_data = admin_get_products(filters)
    
    if products_data and products_data.get('items'):
        st.write(f"Showing {len(products_data['items'])} of {products_data['total']} products")
        
        # Add new product button
        if st.button("➕ Add New Product"):
            st.session_state.admin_editing_product = "new"
            st.rerun()
        
        # Products table
        for product in products_data['items']:
            with st.expander(f"{product['Name']} (SKU: {product['ProductCode']})"):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Price:** ${product.get('Price__c', 'N/A')}")
                    st.write(f"**Category:** {product.get('Family', 'N/A')}")
                    st.write(f"**Status:** {'🟢 Active' if product.get('IsActive') else '🔴 Inactive'}")
                    if product.get('Color__c'):
                        st.write(f"**Color:** {product['Color__c']}")
                    if product.get('Size__c'):
                        st.write(f"**Size:** {product['Size__c']}")
                
                with col2:
                    if st.button("Edit", key=f"edit_{product['Id']}"):
                        st.session_state.admin_editing_product = product['Id']
                        st.rerun()
                
                with col3:
                    if st.button("Delete", key=f"delete_{product['Id']}"):
                        st.session_state.admin_deleting_product = product['Id']
                        st.rerun()
    else:
        st.info("No products found")
        if st.button("➕ Add New Product"):
            st.session_state.admin_editing_product = "new"
            st.rerun()

def admin_product_edit():
    """Admin product edit/create form"""
    st.title("✏️ Product Management")
    
    product_data = None
    if st.session_state.admin_editing_product != "new":
        product_data = admin_get_product(st.session_state.admin_editing_product)
    
    with st.form("product_form"):
        st.write("**Product Information**")
        
        name = st.text_input("Product Name", value=product_data['Name'] if product_data else "")
        product_code = st.text_input("SKU/Product Code", value=product_data['ProductCode'] if product_data else "")
        price = st.number_input("Price ($)", min_value=0.0, value=float(product_data.get('Price__c', 0)) if product_data else 0.0, step=0.01)
        family = st.text_input("Category/Family", value=product_data.get('Family', '') if product_data else "")
        
        col1, col2 = st.columns(2)
        with col1:
            color = st.text_input("Color", value=product_data.get('Color__c', '') if product_data else "")
        with col2:
            size = st.text_input("Size", value=product_data.get('Size__c', '') if product_data else "")
        
        description = st.text_area("Description", value=product_data.get('Description', '') if product_data else "", height=100)
        image_url = st.text_input("Image URL", value=product_data.get('Image_URL__c', '') if product_data else "")
        is_active = st.checkbox("Active", value=product_data.get('IsActive', True) if product_data else True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submit_label = "Update Product" if product_data else "Create Product"
            if st.form_submit_button(submit_label, type="primary"):
                form_data = {
                    "Name": name,
                    "ProductCode": product_code,
                    "Price__c": price,
                    "Family": family,
                    "Description": description,
                    "Color__c": color,
                    "Size__c": size,
                    "Image_URL__c": image_url,
                    "IsActive": is_active
                }
                
                if product_data:
                    # Update existing product
                    result = admin_update_product(st.session_state.admin_editing_product, form_data)
                    if result:
                        st.success("Product updated successfully!")
                        st.session_state.admin_editing_product = None
                        st.rerun()
                else:
                    # Create new product
                    result = admin_create_product(form_data)
                    if result:
                        st.success("Product created successfully!")
                        st.session_state.admin_editing_product = None
                        st.rerun()
        
        with col_btn2:
            if st.form_submit_button("Cancel"):
                st.session_state.admin_editing_product = None
                st.rerun()

def admin_product_delete():
    """Admin product deletion confirmation"""
    st.title("🗑️ Delete Product")
    
    product_data = admin_get_product(st.session_state.admin_deleting_product)
    
    if product_data:
        st.warning(f"Are you sure you want to delete **{product_data['Name']}**?")
        st.write(f"**SKU:** {product_data['ProductCode']}")
        st.write(f"**Price:** ${product_data.get('Price__c', 'N/A')}")
        
        sku_confirmation = st.text_input("Type the SKU to confirm deletion")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Delete", type="primary"):
                if sku_confirmation == product_data['ProductCode']:
                    result = admin_delete_product(st.session_state.admin_deleting_product, sku_confirmation)
                    if result is None:  # 204 No Content
                        st.success("Product deleted successfully!")
                        st.session_state.admin_deleting_product = None
                        st.rerun()
                    else:
                        st.error("Failed to delete product")
                else:
                    st.error("SKU confirmation does not match")
        
        with col2:
            if st.button("Cancel"):
                st.session_state.admin_deleting_product = None
                st.rerun()

def main():
    """Main application"""
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🛍️ E-Commerce Platform")
        
        # View selection
        view_options = ["👨‍💼 Customer Store", "🔧 Admin Panel"]
        selected_view = st.radio("Select View", view_options)
        
        if "Customer Store" in selected_view:
            st.session_state.current_view = "customer"
        else:
            st.session_state.current_view = "admin"
        
        st.write("---")
        
        # Customer navigation
        if st.session_state.current_view == "customer":
            st.subheader("Shopping")
            
            cart_data = get_cart()
            item_count = cart_data.get('item_count', 0) if cart_data else 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("**Shopping Cart**")
            with col2:
                st.write(f"({item_count})")
            
            if st.button("View Cart", use_container_width=True):
                st.session_state.cart_view = True
                st.rerun()
            
            if st.button("Continue Shopping", use_container_width=True):
                if 'cart_view' in st.session_state:
                    del st.session_state.cart_view
                if st.session_state.selected_product:
                    st.session_state.selected_product = None
                st.rerun()
        
        # Admin navigation
        else:
            st.subheader("Admin")
            
            if st.button("Dashboard", use_container_width=True):
                if 'admin_editing_product' in st.session_state:
                    del st.session_state.admin_editing_product
                if 'admin_deleting_product' in st.session_state:
                    del st.session_state.admin_deleting_product
                st.rerun()
            
            if st.button("Manage Products", use_container_width=True):
                if 'admin_editing_product' in st.session_state:
                    del st.session_state.admin_editing_product
                if 'admin_deleting_product' in st.session_state:
                    del st.session_state.admin_deleting_product
                st.rerun()
        
        st.write("---")
        st.write(f"Session: {st.session_state.session_id[:8]}...")
        
        # Health check
        if st.button("Check API Health"):
            health = call_api("/health")
            if health:
                st.success(f"API Status: {health.get('status', 'Unknown')}")
    
    # Main content area
    if st.session_state.current_view == "customer":
        if 'cart_view' in st.session_state and st.session_state.cart_view:
            shopping_cart()
        elif st.session_state.selected_product:
            product_detail_view()
        else:
            customer_home()
    else:
        # Admin views
        if 'admin_editing_product' in st.session_state:
            admin_product_edit()
        elif 'admin_deleting_product' in st.session_state:
            admin_product_delete()
        else:
            admin_dashboard()

if __name__ == "__main__":
    main()