import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Header } from "@/components/Header";
import { ProductCard } from "@/components/ProductCard";
import { Cart } from "@/components/Cart";
import { WhatsAppButton } from "@/components/WhatsAppButton";
import { AdminSidebar } from "@/components/AdminSidebar";
import { ProductDialog } from "@/components/ProductDialog";
import { CheckoutDialog } from "@/components/CheckoutDialog";
import { ProductDetailModal } from "@/components/ProductDetailModal";
import { AdminLoginDialog } from "@/components/AdminLoginDialog";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { productApi, orderApi, cartApi, type CustomerProduct, type Product } from "@/lib/api";
import { Search, Plus, AlertCircle, Filter } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface CartItem {
  product: CustomerProduct;
  quantity: number;
}

const Index = () => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [showAdminLogin, setShowAdminLogin] = useState(false);
  const [adminEmail, setAdminEmail] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [sessionId, setSessionId] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);
  const [adminSection, setAdminSection] = useState("products");
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [deletingProduct, setDeletingProduct] = useState<Product | null>(null);
  const [checkoutDialogOpen, setCheckoutDialogOpen] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<CustomerProduct | null>(null);
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Initialize session on mount (hidden from user)
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await cartApi.getOrCreateSession();
        setSessionId(session.session_id);
        console.log("✅ Session initialized (hidden)");
      } catch (error) {
        console.error("Failed to initialize session:", error);
      }
    };
    initSession();

    // Poll cart every 5 seconds to sync with WhatsApp
    const interval = setInterval(() => {
      if (sessionId && !isAdmin) {
        queryClient.invalidateQueries({ queryKey: ["cart", sessionId] });
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [sessionId, queryClient, isAdmin]);

  // Fetch customer products
  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ["products", searchQuery, selectedCategories, priceRange],
    queryFn: () =>
      productApi.getProducts({
        query: searchQuery || undefined,
        category: selectedCategories.length > 0 ? selectedCategories[0] : undefined,
        price_min: priceRange[0],
        price_max: priceRange[1],
      }),
    enabled: !isAdmin,
  });

  // Fetch cart from backend
  const { data: cartData } = useQuery({
    queryKey: ["cart", sessionId],
    queryFn: () => cartApi.getCart(sessionId),
    enabled: !!sessionId && !isAdmin,
    refetchInterval: 5000,
  });

  // Convert backend cart to frontend format
  const cart: CartItem[] = cartData?.cart?.map((item: any) => ({
    product: {
      id: item.product_id,
      name: item.name,
      price: item.price,
      pricebook_entry_id: item.pricebook_entry_id,
      image_url: item.image_url || "",
      color: item.color || "",
      size: item.size || "",
      description: "",
      product_code: "",
      category: "",
    } as CustomerProduct,
    quantity: item.quantity,
  })) || [];

  // Fetch admin products
  const { data: adminProductsData, isLoading: adminProductsLoading } = useQuery({
    queryKey: ["admin-products"],
    queryFn: () => productApi.adminGetProducts(),
    enabled: isAdmin,
  });

  // Fetch categories
  const { data: categoriesData = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: productApi.getCategories,
  });

  const categories = Array.isArray(categoriesData) ? categoriesData : [];

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: ({ productId, quantity }: { productId: string; quantity: number }) => {
      const product = productsData?.items.find((p) => p.id === productId);
      if (!product) throw new Error("Product not found");
      
      return cartApi.addToCart(sessionId, {
        product_id: product.id,
        quantity,
        pricebook_entry_id: product.pricebook_entry_id,
        price: product.price,
        name: product.name,
        color: product.color,
        size: product.size,
        image_url: product.image_url,
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["cart", sessionId] });
      toast({
        title: "Added to cart",
        description: data.message,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Update cart quantity mutation
  const updateCartMutation = useMutation({
    mutationFn: ({ productId, quantity }: { productId: string; quantity: number }) =>
      cartApi.updateCartItem(sessionId, productId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart", sessionId] });
    },
  });

  // Remove from cart mutation
  const removeFromCartMutation = useMutation({
    mutationFn: (productId: string) => cartApi.removeFromCart(sessionId, productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart", sessionId] });
      toast({ title: "Removed from cart" });
    },
  });

  // Create product mutation
  const createProductMutation = useMutation({
    mutationFn: productApi.adminCreateProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      toast({ title: "Success", description: "Product created successfully" });
      setProductDialogOpen(false);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Update product mutation
  const updateProductMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      productApi.adminUpdateProduct(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      toast({ title: "Success", description: "Product updated successfully" });
      setProductDialogOpen(false);
      setEditingProduct(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Delete product mutation
  const deleteProductMutation = useMutation({
    mutationFn: ({ id, sku }: { id: string; sku: string }) =>
      productApi.adminDeleteProduct(id, sku),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-products"] });
      toast({ title: "Success", description: "Product deleted successfully" });
      setDeletingProduct(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Create order mutation
  const createOrderMutation = useMutation({
    mutationFn: (orderData: any) => orderApi.createOrder(orderData, sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cart", sessionId] });
      toast({
        title: "Order placed!",
        description: "Your order has been placed successfully",
      });
      setCheckoutDialogOpen(false);
      setIsCartOpen(false);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const handleAddToCart = (productId: string, quantity: number = 1) => {
    addToCartMutation.mutate({ productId, quantity });
  };

  const handleUpdateQuantity = (productId: string, quantity: number) => {
    updateCartMutation.mutate({ productId, quantity });
  };

  const handleRemoveFromCart = (productId: string) => {
    removeFromCartMutation.mutate(productId);
  };

  const handleClearFilters = () => {
    setSelectedCategories([]);
    setPriceRange([0, 1000]);
    setSearchQuery("");
  };

  const handleCheckout = () => {
    setCheckoutDialogOpen(true);
  };

  const handleCheckoutSubmit = (data: any) => {
    createOrderMutation.mutate({
      customer: data,
      items: cart.map((item) => ({
        product_id: item.product.id,
        quantity: item.quantity,
        unit_price: item.product.price,
        pricebook_entry_id: item.product.pricebook_entry_id,
      })),
      checkout_source: "Web",
    });
  };

  const handleProductSubmit = (data: any) => {
    if (editingProduct) {
      updateProductMutation.mutate({ id: editingProduct.Id, data });
    } else {
      createProductMutation.mutate(data);
    }
  };

  const handleDeleteProduct = () => {
    if (deletingProduct) {
      deleteProductMutation.mutate({
        id: deletingProduct.Id,
        sku: deletingProduct.ProductCode,
      });
    }
  };

  const handleViewDetails = (product: CustomerProduct) => {
    setSelectedProduct(product);
  };

  // Handle mode toggle - show login dialog for admin
  const handleModeToggle = () => {
    if (!isAdmin) {
      // Switching to admin - show login
      setShowAdminLogin(true);
    } else {
      // Switching back to customer - clear admin session
      setIsAdmin(false);
      setAdminEmail("");
      toast({
        title: "Switched to Customer Mode",
        description: "You are now viewing the customer storefront",
      });
    }
  };

  // Handle admin login
  const handleAdminLogin = (email: string, password: string) => {
    // Demo mode - accept any credentials
    setAdminEmail(email);
    setIsAdmin(true);
    setShowAdminLogin(false);
    
    toast({
      title: "Welcome to Admin Panel",
      description: `Logged in as ${email}`,
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <Header
        onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
        onCartClick={() => setIsCartOpen(true)}
        cartItemCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
        isAdmin={isAdmin}
        onModeToggle={handleModeToggle}
      />

      <div className="flex">
        {isAdmin ? (
          <>
            <AdminSidebar
              activeSection={adminSection}
              onSectionChange={setAdminSection}
            />
            <main className="flex-1 p-6">
              {/* Admin Session Info */}
              <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-blue-700 font-medium">
                    🔒 Admin Session Active - {adminEmail}
                  </span>
                </div>
                <span className="text-xs text-blue-600">
                  Session will reset when server restarts
                </span>
              </div>

              {adminSection === "products" && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold">Products Management</h1>
                    <Button
                      onClick={() => {
                        setEditingProduct(null);
                        setProductDialogOpen(true);
                      }}
                      className="gap-2"
                    >
                      <Plus className="h-4 w-4" />
                      Add Product
                    </Button>
                  </div>

                  {adminProductsLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {[...Array(8)].map((_, i) => (
                        <Skeleton key={i} className="h-80" />
                      ))}
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                      {adminProductsData?.items.map((product) => (
                        <ProductCard
                          key={product.Id}
                          product={product}
                          isAdmin
                          onEdit={(p) => {
                            setEditingProduct(p);
                            setProductDialogOpen(true);
                          }}
                          onDelete={setDeletingProduct}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )}

              {adminSection !== "products" && (
                <div className="flex items-center justify-center h-96">
                  <div className="text-center">
                    <AlertCircle className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
                    <h2 className="text-2xl font-semibold mb-2">Coming Soon</h2>
                    <p className="text-muted-foreground">
                      This section is under development
                    </p>
                  </div>
                </div>
              )}
            </main>
          </>
        ) : (
          <main className="flex-1 p-6">
            {/* Cart Sync Status Badge - NO SESSION ID SHOWN */}
            {sessionId && cart.length > 0 && (
              <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-700 font-medium">
                  🔗 Your cart is synced with WhatsApp
                </span>
              </div>
            )}

            {/* Search and Filter Section */}
            <div className="mb-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                    <Input
                      placeholder="Search products..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button
                    onClick={() => setShowFilters(!showFilters)}
                    variant="outline"
                    className="flex items-center gap-2"
                  >
                    <Filter size={20} />
                    <span>Filters</span>
                  </Button>
                  <Button
                    onClick={() => {}}
                    className="bg-[#96BF48] hover:bg-[#85a840]"
                  >
                    Search
                  </Button>
                </div>

                {showFilters && (
                  <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-[#243746] mb-2">
                        Category
                      </label>
                      <select
                        value={selectedCategories[0] || ""}
                        onChange={(e) => {
                          if (e.target.value) {
                            setSelectedCategories([e.target.value]);
                          } else {
                            setSelectedCategories([]);
                          }
                        }}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#96BF48] focus:border-transparent bg-white"
                      >
                        <option value="">All Categories</option>
                        {categories.map((cat) => (
                          <option key={cat} value={cat}>
                            {cat}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[#243746] mb-2">
                        Min Price
                      </label>
                      <Input
                        type="number"
                        placeholder="0"
                        value={priceRange[0]}
                        onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[#243746] mb-2">
                        Max Price
                      </label>
                      <Input
                        type="number"
                        placeholder="1000"
                        value={priceRange[1]}
                        onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                      />
                    </div>
                  </div>
                )}

                {(searchQuery || selectedCategories.length > 0 || priceRange[0] > 0 || priceRange[1] < 1000) && (
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {productsData?.items.length || 0} results found
                    </span>
                    <button
                      onClick={handleClearFilters}
                      className="text-sm text-[#96BF48] hover:text-[#85a840] font-medium"
                    >
                      Reset filters
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Products Grid */}
            {productsLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {[...Array(8)].map((_, i) => (
                  <Skeleton key={i} className="h-80" />
                ))}
              </div>
            ) : productsData?.items.length === 0 ? (
              <div className="text-center py-20">
                <p className="text-xl text-gray-600">No products found</p>
                <button
                  onClick={handleClearFilters}
                  className="mt-4 text-[#96BF48] hover:text-[#85a840] font-medium"
                >
                  Clear filters
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {productsData?.items.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={handleAddToCart}
                    onViewDetails={handleViewDetails}
                  />
                ))}
              </div>
            )}
          </main>
        )}
      </div>

      <Cart
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cart}
        onUpdateQuantity={handleUpdateQuantity}
        onRemove={handleRemoveFromCart}
        onCheckout={handleCheckout}
      />

      <WhatsAppButton sessionId={sessionId} />

      <Footer />

      {/* Admin Login Dialog */}
      <AdminLoginDialog
        isOpen={showAdminLogin}
        onClose={() => setShowAdminLogin(false)}
        onLogin={handleAdminLogin}
      />

      {selectedProduct && (
        <ProductDetailModal
          product={selectedProduct}
          onClose={() => setSelectedProduct(null)}
          onAddToCart={handleAddToCart}
        />
      )}

      <ProductDialog
        isOpen={productDialogOpen}
        onClose={() => {
          setProductDialogOpen(false);
          setEditingProduct(null);
        }}
        onSubmit={handleProductSubmit}
        product={editingProduct}
        isLoading={
          createProductMutation.isPending || updateProductMutation.isPending
        }
      />

      <CheckoutDialog
        isOpen={checkoutDialogOpen}
        onClose={() => setCheckoutDialogOpen(false)}
        onSubmit={handleCheckoutSubmit}
        isLoading={createOrderMutation.isPending}
      />

      <AlertDialog
        open={!!deletingProduct}
        onOpenChange={() => setDeletingProduct(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Product</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{deletingProduct?.Name}"? This
              action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteProduct}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteProductMutation.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Index;