import { Plus, Edit, Trash2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CustomerProduct, Product } from "@/lib/api";

interface ProductCardProps {
  product: CustomerProduct | Product;
  isAdmin?: boolean;
  onAddToCart?: (productId: string) => void;
  onEdit?: (product: Product) => void;
  onDelete?: (product: Product) => void;
  onView?: (product: Product) => void;
  onViewDetails?: (product: CustomerProduct) => void;
}

export const ProductCard = ({
  product,
  isAdmin = false,
  onAddToCart,
  onEdit,
  onDelete,
  onView,
  onViewDetails,
}: ProductCardProps) => {
  const isCustomerProduct = "pricebook_entry_id" in product;
  
  const name = isCustomerProduct ? product.name : product.Name;
  const price = isCustomerProduct ? product.price : product.Price__c;
  const category = isCustomerProduct ? product.category : product.Family;
  const color = isCustomerProduct ? product.color : product.Color__c;
  const size = isCustomerProduct ? product.size : product.Size__c;
  const imageUrl = isCustomerProduct ? product.image_url : product.Image_URL__c;
  const id = isCustomerProduct ? product.id : product.Id;

  const handleCardClick = () => {
    if (!isAdmin && isCustomerProduct && onViewDetails) {
      onViewDetails(product as CustomerProduct);
    }
  };

  return (
    <Card 
      className={`group overflow-hidden transition-all duration-300 hover:shadow-lg ${!isAdmin ? 'cursor-pointer' : ''}`}
      onClick={!isAdmin ? handleCardClick : undefined}
    >
      <div className="relative aspect-square overflow-hidden bg-muted">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={name}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-110"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-secondary">
            <span className="text-4xl font-bold text-muted-foreground/20">
              {name.charAt(0)}
            </span>
          </div>
        )}
        {category && (
          <Badge className="absolute left-2 top-2">
            {category}
          </Badge>
        )}
      </div>
      <CardContent className="p-4">
        <h3 className="mb-1 font-semibold line-clamp-1">{name}</h3>
        {(color || size) && (
          <p className="mb-2 text-sm text-muted-foreground">
            {[color, size].filter(Boolean).join(" • ")}
          </p>
        )}
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-primary">
            ${price?.toFixed(2) || "0.00"}
          </span>
          {isAdmin ? (
            <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={(e) => {
                  e.stopPropagation();
                  onView?.(product as Product);
                }}
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit?.(product as Product);
                }}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-destructive hover:text-destructive"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete?.(product as Product);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <Button
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onAddToCart?.(id);
              }}
              className="gap-1"
            >
              <Plus className="h-4 w-4" />
              Add
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};