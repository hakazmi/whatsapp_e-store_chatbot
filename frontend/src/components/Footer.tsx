import { Facebook, Instagram, Twitter, Mail, Phone, MapPin } from "lucide-react";
import { Separator } from "./ui/separator";

export const Footer = () => {
  return (
    <footer className="bg-gradient-to-br from-background via-background to-primary/5 border-t border-border/50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Company Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">About Us</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Your trusted partner for quality products and exceptional service. We deliver excellence right to your doorstep.
            </p>
            <div className="flex gap-3 pt-2">
              <a 
                href="#" 
                className="w-10 h-10 rounded-full bg-primary/10 hover:bg-primary/20 flex items-center justify-center transition-colors group"
                aria-label="Facebook"
              >
                <Facebook className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
              </a>
              <a 
                href="#" 
                className="w-10 h-10 rounded-full bg-primary/10 hover:bg-primary/20 flex items-center justify-center transition-colors group"
                aria-label="Instagram"
              >
                <Instagram className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
              </a>
              <a 
                href="#" 
                className="w-10 h-10 rounded-full bg-primary/10 hover:bg-primary/20 flex items-center justify-center transition-colors group"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Quick Links</h3>
            <ul className="space-y-2">
              {["Shop All", "New Arrivals", "Best Sellers", "Sale", "Gift Cards"].map((link) => (
                <li key={link}>
                  <a 
                    href="#" 
                    className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center group"
                  >
                    <span className="group-hover:translate-x-1 transition-transform">{link}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Customer Service */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Customer Service</h3>
            <ul className="space-y-2">
              {["Contact Us", "Track Order", "Returns & Exchanges", "Shipping Info", "FAQ"].map((link) => (
                <li key={link}>
                  <a 
                    href="#" 
                    className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center group"
                  >
                    <span className="group-hover:translate-x-1 transition-transform">{link}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Contact Info</h3>
            <ul className="space-y-3">
              <li className="flex items-start gap-3 text-sm text-muted-foreground">
                <MapPin className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                <span>123 Store Street, City, State 12345</span>
              </li>
              <li className="flex items-center gap-3 text-sm text-muted-foreground">
                <Phone className="w-5 h-5 text-primary flex-shrink-0" />
                <a href="tel:+1234567890" className="hover:text-primary transition-colors">
                  +1 (234) 567-890
                </a>
              </li>
              <li className="flex items-center gap-3 text-sm text-muted-foreground">
                <Mail className="w-5 h-5 text-primary flex-shrink-0" />
                <a href="mailto:support@store.com" className="hover:text-primary transition-colors">
                  support@store.com
                </a>
              </li>
            </ul>
          </div>
        </div>

        <Separator className="my-8 bg-border/50" />

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-muted-foreground text-center md:text-left">
            © {new Date().getFullYear()} E-Store. All rights reserved.
          </p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-primary transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-primary transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-primary transition-colors">
              Cookie Policy
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
