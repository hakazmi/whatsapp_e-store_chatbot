import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  categories: string[];
  selectedCategories: string[];
  onCategoryChange: (category: string) => void;
  priceRange: [number, number];
  onPriceRangeChange: (value: [number, number]) => void;
  colors: string[];
  selectedColors: string[];
  onColorChange: (color: string) => void;
  sizes: string[];
  selectedSizes: string[];
  onSizeChange: (size: string) => void;
  onClearFilters: () => void;
}

export const Sidebar = ({
  isOpen,
  onClose,
  categories,
  selectedCategories,
  onCategoryChange,
  priceRange,
  onPriceRangeChange,
  colors,
  selectedColors,
  onColorChange,
  sizes,
  selectedSizes,
  onSizeChange,
  onClearFilters,
}: SidebarProps) => {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 h-full w-80 border-r border-border bg-background transition-transform duration-300 lg:sticky lg:top-16 lg:h-[calc(100vh-4rem)] lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border p-4">
            <h2 className="text-lg font-semibold">Filters</h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="lg:hidden"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Content */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-6">
              {/* Categories */}
              <div>
                <h3 className="mb-3 text-sm font-semibold">Categories</h3>
                <div className="space-y-2">
                  {categories.map((category) => (
                    <div key={category} className="flex items-center space-x-2">
                      <Checkbox
                        id={`category-${category}`}
                        checked={selectedCategories.includes(category)}
                        onCheckedChange={() => onCategoryChange(category)}
                      />
                      <Label
                        htmlFor={`category-${category}`}
                        className="text-sm cursor-pointer"
                      >
                        {category}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <Separator />

              {/* Price Range */}
              <div>
                <h3 className="mb-3 text-sm font-semibold">Price Range</h3>
                <div className="space-y-4">
                  <Slider
                    value={priceRange}
                    onValueChange={onPriceRangeChange}
                    min={0}
                    max={1000}
                    step={10}
                    className="w-full"
                  />
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span>${priceRange[0]}</span>
                    <span>${priceRange[1]}</span>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Colors */}
              {colors.length > 0 && (
                <>
                  <div>
                    <h3 className="mb-3 text-sm font-semibold">Colors</h3>
                    <div className="space-y-2">
                      {colors.map((color) => (
                        <div key={color} className="flex items-center space-x-2">
                          <Checkbox
                            id={`color-${color}`}
                            checked={selectedColors.includes(color)}
                            onCheckedChange={() => onColorChange(color)}
                          />
                          <Label
                            htmlFor={`color-${color}`}
                            className="text-sm cursor-pointer"
                          >
                            {color}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </div>
                  <Separator />
                </>
              )}

              {/* Sizes */}
              {sizes.length > 0 && (
                <div>
                  <h3 className="mb-3 text-sm font-semibold">Sizes</h3>
                  <div className="flex flex-wrap gap-2">
                    {sizes.map((size) => (
                      <Button
                        key={size}
                        variant={selectedSizes.includes(size) ? "default" : "outline"}
                        size="sm"
                        onClick={() => onSizeChange(size)}
                      >
                        {size}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>

          {/* Footer */}
          <div className="border-t border-border p-4">
            <Button
              variant="outline"
              className="w-full"
              onClick={onClearFilters}
            >
              Clear Filters
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
};
