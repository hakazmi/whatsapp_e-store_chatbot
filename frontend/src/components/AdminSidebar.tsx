import {
  LayoutDashboard,
  Package,
  ShoppingBag,
  Users,
  BarChart3,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AdminSidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const menuItems = [
  { id: "dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { id: "products", icon: Package, label: "Products" },
  { id: "orders", icon: ShoppingBag, label: "Orders" },
  { id: "customers", icon: Users, label: "Customers" },
  { id: "analytics", icon: BarChart3, label: "Analytics" },
  { id: "settings", icon: Settings, label: "Settings" },
];

export const AdminSidebar = ({
  activeSection,
  onSectionChange,
}: AdminSidebarProps) => {
  return (
    <aside className="hidden lg:flex w-64 flex-col border-r border-border bg-background">
      <div className="flex-1 overflow-y-auto py-4">
        <nav className="space-y-1 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSectionChange(item.id)}
                className={cn(
                  "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};