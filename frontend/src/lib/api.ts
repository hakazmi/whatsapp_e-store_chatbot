/**
 * Enhanced API client with cart synchronization
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const WHATSAPP_API_URL = import.meta.env.VITE_WHATSAPP_API_URL || 'http://localhost:5000';

export interface Product {
  Id: string;
  Name: string;
  ProductCode: string;
  Price__c: number;
  Family: string;
  Description?: string;
  Color__c?: string;
  Size__c?: string;
  Image_URL__c?: string;
  IsActive: boolean;
  CreatedDate?: string;
  LastModifiedDate?: string;
}

export interface CustomerProduct {
  id: string;
  name: string;
  price: number;
  description: string;
  color: string;
  size: string;
  product_code: string;
  category: string;
  image_url: string;
  pricebook_entry_id: string;
}

export interface CartItemAdd {
  product_id: string;
  quantity: number;
  pricebook_entry_id: string;
  price: number;
  name: string;
  color?: string;
  size?: string;
  image_url?: string;
}

export interface OrderRequest {
  customer: {
    name: string;
    email: string;
    phone?: string;
  };
  items: Array<{
    product_id: string;
    quantity: number;
    unit_price: number;
    pricebook_entry_id: string;
  }>;
  checkout_source?: string;
}

export interface ProductCreateRequest {
  Name: string;
  ProductCode: string;
  Price__c: number;
  Family: string;
  Description?: string;
  Color__c?: string;
  Size__c?: string;
  Image_URL__c?: string;
  IsActive?: boolean;
}

// Product APIs
export const productApi = {
  // Customer-facing APIs
  getProducts: async (params?: {
    page?: number;
    page_size?: number;
    query?: string;
    category?: string;
    price_min?: number;
    price_max?: number;
    color?: string;
    size?: string;
  }): Promise<{ items: CustomerProduct[]; page: number; page_size: number; total: number }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const response = await fetch(`${API_BASE_URL}/products?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch products');
    const data = await response.json();
    return {
      items: Array.isArray(data) ? data : data.items || [],
      page: 1,
      page_size: 50,
      total: Array.isArray(data) ? data.length : data.total || 0
    };
  },

  getProductById: async (id: string): Promise<CustomerProduct> => {
    const response = await fetch(`${API_BASE_URL}/products/${id}`);
    if (!response.ok) throw new Error('Failed to fetch product');
    return response.json();
  },

  getCategories: async (): Promise<string[]> => {
    const response = await fetch(`${API_BASE_URL}/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    const data = await response.json();
    return data.categories || [];
  },

  // Admin APIs
  adminGetProducts: async (params?: {
    page?: number;
    page_size?: number;
    category?: string;
    active?: boolean;
  }): Promise<{ items: Product[]; page: number; page_size: number; total: number }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    const response = await fetch(`${API_BASE_URL}/admin/products?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch admin products');
    return response.json();
  },

  adminCreateProduct: async (product: ProductCreateRequest): Promise<Product> => {
    const response = await fetch(`${API_BASE_URL}/admin/products`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create product');
    }
    return response.json();
  },

  adminUpdateProduct: async (id: string, product: Partial<ProductCreateRequest>): Promise<Product> => {
    const response = await fetch(`${API_BASE_URL}/admin/products/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(product),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update product');
    }
    return response.json();
  },

  adminDeleteProduct: async (id: string, sku: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/admin/products/${id}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sku_confirmation: sku }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete product');
    }
  },
};

// Cart APIs - Enhanced with session support
export const cartApi = {
  getOrCreateSession: async (phone?: string): Promise<{ session_id: string; cart: any[]; total: number }> => {
    const queryParams = phone ? `?phone=${encodeURIComponent(phone)}` : '';
    const response = await fetch(`${API_BASE_URL}/cart/session${queryParams}`, {
      credentials: 'include', // Include cookies
    });
    if (!response.ok) throw new Error('Failed to get session');
    return response.json();
  },

  getCart: async (sessionId: string): Promise<{ cart: any[]; total: number; item_count: number }> => {
    const response = await fetch(`${API_BASE_URL}/cart/${sessionId}`);
    if (!response.ok) throw new Error('Failed to fetch cart');
    return response.json();
  },

  addToCart: async (sessionId: string, item: CartItemAdd): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/cart/${sessionId}/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add to cart');
    }
    return response.json();
  },

  updateCartItem: async (sessionId: string, productId: string, quantity: number): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/cart/${sessionId}/item/${productId}?quantity=${quantity}`, {
      method: 'PUT',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update cart');
    }
    return response.json();
  },

  removeFromCart: async (sessionId: string, productId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/cart/${sessionId}/item/${productId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to remove from cart');
    }
    return response.json();
  },

  clearCart: async (sessionId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/cart/${sessionId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to clear cart');
    }
    return response.json();
  },
};

// Order APIs - Enhanced with session support
export const orderApi = {
  createOrder: async (order: OrderRequest, sessionId?: string): Promise<any> => {
    const queryParams = sessionId ? `?session_id=${sessionId}` : '';
    const response = await fetch(`${API_BASE_URL}/orders${queryParams}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(order),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create order');
    }
    return response.json();
  },

  getCustomerOrders: async (email: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/orders/customer/${email}`);
    if (!response.ok) throw new Error('Failed to fetch orders');
    return response.json();
  },
};

// WhatsApp APIs
export const whatsappApi = {
  sendMessage: async (data: { to: string; message: string }): Promise<any> => {
    const response = await fetch(`${WHATSAPP_API_URL}/test/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send message');
    }
    return response.json();
  },

  getThreads: async (): Promise<any> => {
    const response = await fetch(`${WHATSAPP_API_URL}/threads`);
    if (!response.ok) throw new Error('Failed to fetch threads');
    return response.json();
  },

  getSyncStatus: async (phone: string): Promise<any> => {
    const response = await fetch(`${WHATSAPP_API_URL}/sync-status/${phone}`);
    if (!response.ok) throw new Error('Failed to fetch sync status');
    return response.json();
  },

  linkSession: async (phone: string, sessionId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/whatsapp/link-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, session_id: sessionId }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to link session');
    }
    return response.json();
  },
};