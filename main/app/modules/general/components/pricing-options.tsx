"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PricingCards } from "@/components/ui/pricing-cards";
import getStripe from "@/lib/utils/stripe/stripe";
import { fetchPostJSON } from "@/lib/utils/stripe/stripe-helpers";

// Типы для интервалов подписки
type PlanInterval = 'monthly' | 'yearly';

export default function PricingPage() {
  const [openDialog, setOpenDialog] = useState(false);
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [interval, setInterval] = useState<PlanInterval>('monthly');

  // Обработчик изменения интервала в UI компоненте
  const handleIntervalChange = (newInterval: string) => {
    setInterval(newInterval as PlanInterval);
  };

  const handleSubscription = async (packageName: string) => {
    try {
      setLoadingTier(packageName);
      
      if (packageName === 'Teams') {
        setTimeout(() => {
          setLoadingTier(null);
          toast.success(`Successfully subscribed to ${packageName} plan!`);
          setOpenDialog(false);
        }, 1500);
        return;
      }

      // ID цен для разных пакетов и интервалов
      const priceIds = {
        Starter: {
          monthly: 'price_1OxVblD7STfJJkPfuQFD58qG',
          yearly: 'price_1OxYOuD7STfJJkPf3VzpHGQx'
        },
        Pro: {
          monthly: 'price_1RB5i6IuFYxu6EyPqdW56iPr',
          yearly: 'price_1RB5mUIuFYxu6EyPb2Oxmsck'
        }
      };

      // Получаем price ID в зависимости от пакета и интервала
      const priceId = priceIds[packageName as keyof typeof priceIds]?.[interval];
      
      if (!priceId) {
        toast.error('Invalid package selection');
        setLoadingTier(null);
        return;
      }

      const response = await fetchPostJSON('/api/stripe/checkout_sessions', {
        priceId
      });

      if (response.statusCode === 500) {
        console.error(response.message);
        toast.error('Payment failed. Please try again later.');
        setLoadingTier(null);
        return;
      }

      const stripe = await getStripe();
      const { error } = await stripe!.redirectToCheckout({
        sessionId: response.sessionId,
      });
      
      if (error) {
        console.warn(error.message);
        toast.error(error.message || 'Payment failed. Please try again.');
      }
      
      setLoadingTier(null);
    } catch (error) {
      console.error('Error:', error);
      toast.error('Something went wrong. Please try again later.');
      setLoadingTier(null);
    }
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
        { name: "Unlimited Messages", included: true },
        { name: "10 Active Flows", included: true },
        { name: "Rent providers API keys", included: false },
        { name: "Custom integrations", included: false }
      ],
      cta: {
        text: loadingTier === "Starter" ? "Processing..." : "Choose Starter",
        onClick: () => handleSubscription("Starter")
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
        { name: "Unlimited Messages", included: true },
        { name: "30 Active Flows", included: true },
        { name: "Rent providers API keys", included: true },
        { name: "Custom integrations", included: true }
      ],
      cta: {
        text: loadingTier === "Pro" ? "Processing..." : "Choose Pro",
        onClick: () => handleSubscription("Pro")
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