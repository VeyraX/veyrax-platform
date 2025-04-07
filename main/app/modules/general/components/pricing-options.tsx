"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PricingCards } from "@/components/ui/pricing-cards";
import getStripe from "@/lib/utils/stripe/stripe";
import { fetchPostJSON } from "@/lib/utils/stripe/stripe-helpers";
import {
  pricingPlans,
  getSimpleFeatures,
  type PlanInterval,
  getPriceId
} from "./pricing-data";

interface PricingTier {
  name: string;
  price: { monthly: number; yearly: number } | number;
  interval?: string;
  description: string;
  highlight?: boolean;
  features: { name: string; included: boolean }[];
  cta: {
    text: string;
    onClick: () => void;
  };
}

export default function PricingPage() {
  const [openDialog, setOpenDialog] = useState(false);
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [interval, setInterval] = useState<PlanInterval>('monthly');

  const handleSubscription = async (planId: string) => {
    try {
      setLoadingTier(planId);
      
      if (planId === 'teams') {
        setTimeout(() => {
          setLoadingTier(null);
          toast.success(`Successfully submitted request for Teams plan!`);
          setOpenDialog(false);
        }, 1500);
        return;
      }

      // Get price ID for the current plan and interval
      const priceId = getPriceId(planId, interval);
      
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

  // Convert our pricing data to the format expected by PricingCards
  const pricingTiers: PricingTier[] = pricingPlans
    .filter(plan => plan.id !== 'free')
    .map(plan => ({
      name: plan.name,
      price: plan.id === 'teams' ? 0 : plan.price,
      interval: plan.id === 'teams' ? "Custom pricing" : undefined,
      description: plan.description,
      highlight: plan.highlight,
      // Map features to PricingCards expected format
      features: getSimpleFeatures(plan).map(feature => ({
        name: feature.name,
        included: feature.included === true || typeof feature.included === 'string'
      })),
      cta: {
        text: loadingTier === plan.id ? "Processing..." : plan.buttonText,
        onClick: () => handleSubscription(plan.id)
      }
    }));

  return (
    <>
      <PricingCards 
        tiers={pricingTiers}
        className="grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
        containerClassName="max-w-6xl"
        defaultInterval="monthly"
      />
      
      <Dialog open={openDialog} onOpenChange={setOpenDialog}>
        <DialogContent className="max-w-6xl w-[95vw]">
          <DialogHeader>
            <DialogTitle>Choose a Subscription Plan</DialogTitle>
          </DialogHeader>
          <PricingCards 
            tiers={pricingTiers}
            className="grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
            sectionClassName="py-0"
            containerClassName="px-0 mx-0"
            defaultInterval="monthly"
          />
        </DialogContent>
      </Dialog>
    </>
  );
}