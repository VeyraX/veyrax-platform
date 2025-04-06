"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PricingCards } from "@/components/ui/pricing-cards";

export default function PricingPage() {
  const [openDialog, setOpenDialog] = useState(false);
  const [loadingTier, setLoadingTier] = useState<string | null>(null);

  const handleSubscription = (packageName: string) => {
    setLoadingTier(packageName);
    setTimeout(() => {
      setLoadingTier(null);
      toast.success(`Successfully subscribed to ${packageName} plan!`);
      setOpenDialog(false);
    }, 1500);
  };

  const pricingTiers = [
    {
      name: "Starter",
      price: {
        monthly: 12,
        yearly: 8
      },
      description: "Just to get started",
      highlight: false,
      features: [
        { name: "600 API requests", included: true },
        { name: "Unlimited Chats", included: true },
        { name: "10 Active Flows", included: true },
        { name: "Rent providers API keys", included: false },
        { name: "Custom integrations", included: false }
      ],
      cta: {
        text: loadingTier === "Premium" ? "Processing..." : "Choose Premium",
        onClick: () => handleSubscription("Premium")
      }
    },
    {
      name: "Pro",
      price: {
        monthly: 40,
        yearly: 32
      },
      description: "For power users who need more",
      highlight: true,
      features: [
        { name: "1,500 API requests", included: true },
        { name: "Unlimited Chats", included: true },
        { name: "30 Active Flows", included: true },
        { name: "Rent providers API keys", included: true },
        { name: "Custom integrations", included: true }
      ],
      cta: {
        text: loadingTier === "Premium" ? "Processing..." : "Choose Premium",
        onClick: () => handleSubscription("Premium")
      }
    },
    {
      name: "Teams",
      price: 0,
      interval: "Custom pricing",
      description: "For production Agents who need tools and customization",
      features: [
        { name: "Custom API calls", included: true },
        { name: "Custom flows", included: true },
        { name: "Custom branding", included: true },
        { name: "Dedicated account manager", included: true }
      ],
      cta: {
        text: "Contact Sales",
        onClick: () => handleSubscription("Teams")
      }
    }
  ];

  return (
    <>
      <PricingCards 
        tiers={pricingTiers}
        className="md:grid-cols-3"
        containerClassName="max-w-6xl"
        defaultInterval="monthly"
      />
      
      {/* This dialog would be used if you needed a modal version */}
      <Dialog open={openDialog} onOpenChange={setOpenDialog}>
        <DialogContent className="max-w-6xl w-[95vw]">
          <DialogHeader>
            <DialogTitle>Choose a Subscription Plan</DialogTitle>
          </DialogHeader>
          <PricingCards 
            tiers={pricingTiers}
            className="md:grid-cols-3"
            sectionClassName="py-0"
            containerClassName="px-0 mx-0"
            defaultInterval="monthly"
          />
        </DialogContent>
      </Dialog>
    </>
  );
}