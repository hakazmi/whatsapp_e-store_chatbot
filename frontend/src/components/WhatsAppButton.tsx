import { Button } from "@/components/ui/button";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface WhatsAppButtonProps {
  sessionId?: string;
}

export const WhatsAppButton = ({ sessionId }: WhatsAppButtonProps) => {
  const [showDialog, setShowDialog] = useState(false);

  // Twilio Sandbox WhatsApp number
  const whatsappNumber = "14155238886";

  const handleStartChat = async () => {
    if (sessionId) {
      try {
        await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/whatsapp/prepare-session`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            timestamp: Date.now(),
          }),
        });
        console.log("✅ Session prepared for WhatsApp link");
      } catch (error) {
        console.error("Failed to prepare session:", error);
      }
    }

    const message = encodeURIComponent("Hi! I want to shop for products.");
    const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${message}`;
    window.open(whatsappUrl, "_blank");
    setShowDialog(false);
  };

  return (
    <>
      {/* Floating WhatsApp Button */}
      <Button
        size="lg"
        className="fixed bottom-6 right-6 z-50 h-16 w-16 rounded-full p-0 shadow-2xl bg-[#25D366] hover:bg-[#128C7E] animate-bounce hover:animate-none transition-all duration-300 flex items-center justify-center"
        onClick={() => setShowDialog(true)}
        title="Chat with us on WhatsApp"
      >
        {/* ✅ Larger WhatsApp Logo */}
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 32 32"
          fill="white"
          className="h-10 w-10"  // increased from 8x8 → 10x10
        >
          <path d="M16.003 3C9.373 3 4 8.373 4 15c0 2.553.79 4.923 2.145 6.886L4 29l7.273-2.084C13.026 27.618 14.481 28 16 28c6.627 0 12-5.373 12-12S22.63 3 16.003 3zm-.003 22.5c-1.351 0-2.68-.347-3.854-1.006l-.276-.158-4.318 1.237 1.232-4.208-.179-.288A8.985 8.985 0 0 1 7 15c0-4.971 4.029-9 9.003-9 4.973 0 9.002 4.029 9.002 9s-4.029 9.5-9.002 9.5zm4.962-6.603c-.272-.136-1.606-.79-1.855-.88-.25-.09-.43-.136-.61.136s-.7.88-.857 1.06-.316.204-.588.068c-.272-.136-1.146-.421-2.183-1.341-.806-.719-1.35-1.606-1.508-1.878-.157-.272-.017-.42.12-.556.123-.123.272-.316.408-.474.136-.158.181-.272.272-.454.09-.181.045-.34-.022-.475-.068-.136-.61-1.475-.837-2.016-.22-.527-.445-.455-.61-.464-.157-.008-.34-.01-.522-.01a1.007 1.007 0 0 0-.727.34c-.25.272-.953.93-.953 2.265s.975 2.627 1.112 2.812c.136.181 1.917 2.932 4.65 4.109.65.28 1.157.447 1.552.573.652.208 1.244.179 1.713.109.523-.078 1.606-.655 1.833-1.287.227-.63.227-1.172.159-1.287-.068-.113-.25-.18-.523-.317z" />
        </svg>
      </Button>

      {/* WhatsApp Link Dialog */}
      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {/* Medium-sized logo in header */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 32 32"
                fill="#25D366"
                className="h-6 w-6"
              >
                <path d="M16.003 3C9.373 3 4 8.373 4 15c0 2.553.79 4.923 2.145 6.886L4 29l7.273-2.084C13.026 27.618 14.481 28 16 28c6.627 0 12-5.373 12-12S22.63 3 16.003 3zm-.003 22.5c-1.351 0-2.68-.347-3.854-1.006l-.276-.158-4.318 1.237 1.232-4.208-.179-.288A8.985 8.985 0 0 1 7 15c0-4.971 4.029-9 9.003-9 4.973 0 9.002 4.029 9.002 9s-4.029 9.5-9.002 9.5zm4.962-6.603c-.272-.136-1.606-.79-1.855-.88-.25-.09-.43-.136-.61.136s-.7.88-.857 1.06-.316.204-.588.068c-.272-.136-1.146-.421-2.183-1.341-.806-.719-1.35-1.606-1.508-1.878-.157-.272-.017-.42.12-.556.123-.123.272-.316.408-.474.136-.158.181-.272.272-.454.09-.181.045-.34-.022-.475-.068-.136-.61-1.475-.837-2.016-.22-.527-.445-.455-.61-.464-.157-.008-.34-.01-.522-.01a1.007 1.007 0 0 0-.727.34c-.25.272-.953.93-.953 2.265s.975 2.627 1.112 2.812c.136.181 1.917 2.932 4.65 4.109.65.28 1.157.447 1.552.573.652.208 1.244.179 1.713.109.523-.078 1.606-.655 1.833-1.287.227-.63.227-1.172.159-1.287-.068-.113-.25-.18-.523-.317z" />
              </svg>
              Chat on WhatsApp
            </DialogTitle>
            <DialogDescription>
              Continue shopping with your cart synced automatically!
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-700 font-medium mb-2">
                🔗 Your cart will sync automatically
              </p>
              <p className="text-xs text-green-600">
                Just click and start chatting - everything is linked!
              </p>
            </div>

            {/* Main Start Chat Button */}
            <Button
              onClick={handleStartChat}
              className="w-full bg-[#25D366] hover:bg-[#128C7E] h-12"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 32 32"
                fill="white"
                className="h-6 w-6 mr-2"
              >
                <path d="M16.003 3C9.373 3 4 8.373 4 15c0 2.553.79 4.923 2.145 6.886L4 29l7.273-2.084C13.026 27.618 14.481 28 16 28c6.627 0 12-5.373 12-12S22.63 3 16.003 3zm-.003 22.5c-1.351 0-2.68-.347-3.854-1.006l-.276-.158-4.318 1.237 1.232-4.208-.179-.288A8.985 8.985 0 0 1 7 15c0-4.971 4.029-9 9.003-9 4.973 0 9.002 4.029 9.002 9s-4.029 9.5-9.002 9.5zm4.962-6.603c-.272-.136-1.606-.79-1.855-.88-.25-.09-.43-.136-.61.136s-.7.88-.857 1.06-.316.204-.588.068c-.272-.136-1.146-.421-2.183-1.341-.806-.719-1.35-1.606-1.508-1.878-.157-.272-.017-.42.12-.556.123-.123.272-.316.408-.474.136-.158.181-.272.272-.454.09-.181.045-.34-.022-.475-.068-.136-.61-1.475-.837-2.016-.22-.527-.445-.455-.61-.464-.157-.008-.34-.01-.522-.01a1.007 1.007 0 0 0-.727.34c-.25.272-.953.93-.953 2.265s.975 2.627 1.112 2.812c.136.181 1.917 2.932 4.65 4.109.65.28 1.157.447 1.552.573.652.208 1.244.179 1.713.109.523-.078 1.606-.655 1.833-1.287.227-.63.227-1.172.159-1.287-.068-.113-.25-.18-.523-.317z" />
              </svg>
              Start Shopping on WhatsApp
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        .animate-bounce {
          animation: bounce 2s infinite;
        }
      `}</style>
    </>
  );
};

