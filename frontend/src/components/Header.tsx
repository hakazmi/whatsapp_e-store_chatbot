import { ShoppingCart, Heart, User, Menu, Store, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link } from "react-router-dom";
import { useState } from "react";

interface HeaderProps {
  onMenuClick: () => void;
  onCartClick: () => void;
  cartItemCount: number;
  isAdmin: boolean;
  onModeToggle: () => void;
}

export const Header = ({
  onMenuClick,
  onCartClick,
  cartItemCount,
  isAdmin,
  onModeToggle,
}: HeaderProps) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleMenuClick = () => {
    setSidebarOpen(!sidebarOpen);
    onMenuClick();
  };

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          {/* Left side */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleMenuClick}
              className="text-gray-700"
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex items-center gap-3 flex-shrink-0">
                <img
                  src="https://upload.wikimedia.org/wikipedia/commons/0/0e/Shopify_logo_2018.svg"
                  alt="Shopify Logo"
                  className="h-7 w-auto"
                />
              </div>
            <nav className="hidden lg:flex items-center gap-6 ml-6">
              <Link
                to="/"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Products
              </Link>
              <Link
                to="/deals"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Deals
              </Link>
              <Link
                to="/about"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                About
              </Link>
              <Link
                to="/contact"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Contact
              </Link>
            </nav>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            {!isAdmin && (
              <>
                <Button variant="ghost" size="icon" className="hidden sm:flex">
                  <Heart className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon" className="hidden sm:flex">
                  <User className="h-5 w-5" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onCartClick}
                  className="relative"
                >
                  <ShoppingCart className="h-5 w-5" />
                  {cartItemCount > 0 && (
                    <Badge
                      variant="destructive"
                      className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs"
                    >
                      {cartItemCount}
                    </Badge>
                  )}
                </Button>
              </>
            )}
            <Button
              variant={isAdmin ? "default" : "outline"}
              size="sm"
              onClick={onModeToggle}
              className="ml-2"
            >
              {isAdmin ? "Customer Mode" : "Admin Panel"}
            </Button>
          </div>
        </div>
      </header>

      {/* Sidebar Menu */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40">
          {/* Overlay */}
          <div
            className="absolute inset-0 bg-black bg-opacity-50"
            onClick={handleMenuClick}
          />

          {/* Sidebar Panel */}
          <div className="absolute left-0 top-0 h-full w-80 bg-white shadow-2xl flex flex-col">
            {/* Sidebar Header */}
            <div className="flex-shrink-0 flex items-center justify-between p-6 border-b border-gray-200 bg-white">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary">
                  <Store className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-bold text-foreground">ShopHub</span>
              </div>
              <button
                onClick={handleMenuClick}
                className="p-2 hover:bg-gray-50 rounded-full transition-colors text-gray-700"
              >
                <X size={24} />
              </button>
            </div>

            {/* Scrollable Sidebar Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6 space-y-8">
                {/* New Arrival Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4 flex items-center gap-2">
                    <div className="w-2 h-2 bg-[#96BF48] rounded-full"></div>
                    New Arrival
                  </h3>
                  <div className="space-y-2">
                    {[
                      'Spring Collection 2025',
                      'Limited Edition',
                      'Just Landed',
                      'Summer Essentials',
                      'Back to School',
                    ].map((item) => (
                      <a
                        key={item}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {item}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Collections Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">Collections</h3>
                  <div className="space-y-2">
                    {[
                      "Men's Fashion",
                      "Women's Wear",
                      'Kids & Babies',
                      'Home & Living',
                      'Electronics',
                      'Sports & Outdoors',
                      'Beauty & Personal Care',
                    ].map((item) => (
                      <a
                        key={item}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {item}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Brands Section */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">Popular Brands</h3>
                  <div className="space-y-2">
                    {[
                      'Nike',
                      'Adidas',
                      'Zara',
                      'H&M',
                      'Apple',
                      'Samsung',
                      'Sony',
                      "Levi's",
                      'Puma',
                    ].map((brand) => (
                      <a
                        key={brand}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {brand}
                      </a>
                    ))}
                  </div>
                </div>

                {/* Additional Categories */}
                <div>
                  <h3 className="text-lg font-semibold text-[#243746] mb-4">More Categories</h3>
                  <div className="space-y-2">
                    {[
                      'Sale & Clearance',
                      'Best Sellers',
                      'Gift Cards',
                      'Customer Favorites',
                    ].map((cat) => (
                      <a
                        key={cat}
                        href="#"
                        className="block px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-[#96BF48] rounded-lg transition-colors border-l-4 border-transparent hover:border-[#96BF48]"
                      >
                        {cat}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};