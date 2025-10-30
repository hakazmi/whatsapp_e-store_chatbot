export interface Product {
  Id: string;
  Name: string;
  ProductCode: string;
  Price__c: number;
  Family: string;
  Description?: string;
  Color__c?: string;
  Size__c?: string;
  StockQuantity__c?: number;
  ImageURL__c?: string;
  IsActive: boolean;
}

export interface CartItem extends Product {
  quantity: number;
}

export interface FilterState {
  category: string;
  priceRange: [number, number];
  colors: string[];
  sizes: string[];
  search: string;
}
