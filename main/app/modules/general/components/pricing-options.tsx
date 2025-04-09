"use client";

import { useState } from "react";
import { toast } from "sonner";
import { PricingCards } from "@/components/ui/pricing-cards";
import getStripe from "@/lib/utils/stripe/stripe";
import { fetchPostJSON } from "@/lib/utils/stripe/stripe-helpers";
import { TeamRequestDialog } from "./team-request-dialog";
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
  features: { name: string; included: boolean; tooltip?: string }[];
  cta: {
    text: string;
    onClick: () => void;
  };
}

export default function PricingPage() {
  const [openTeamDialog, setOpenTeamDialog] = useState(false);
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [interval, setInterval] = useState<PlanInterval>('yearly');

  const handleSubscription = async (planId: string) => {
    try {
      setLoadingTier(planId);
      
      if (planId === 'teams') {
        setOpenTeamDialog(true);
        setLoadingTier(null);
        return;
      }

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

  const pricingTiers: PricingTier[] = pricingPlans
    .filter(plan => plan.id !== 'free')
    .map(plan => ({
      name: plan.name,
      price: plan.id === 'teams' ? 0 : plan.price,
      interval: plan.id === 'teams' ? "Custom pricing" : undefined,
      description: plan.description,
      highlight: plan.highlight,
      features: getSimpleFeatures(plan).map(feature => ({
        name: feature.name,
        included: feature.included === true || typeof feature.included === 'string',
        tooltip: feature.tooltip
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
        sectionClassName="py-0"
        defaultInterval={interval}
        title="Empower your agents and workflows with 1000+ actions"
        description="Get higher limits, custom integrations and more with VeyraX."
        onIntervalChange={(newInterval: "monthly" | "yearly") => setInterval(newInterval as PlanInterval)}
      />

      <TeamRequestDialog open={openTeamDialog} onOpenChange={setOpenTeamDialog} />
    </>
  );
}