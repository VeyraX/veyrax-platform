"use client";

import * as React from "react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs-updated";
import { Check, Minus, MoveRight, PhoneCall, InfoIcon } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import NumberFlow from "@number-flow/react";
import getStripe from "@/lib/utils/stripe/stripe";
import { fetchPostJSON } from "@/lib/utils/stripe/stripe-helpers";
import { TeamRequestDialog } from "./team-request-dialog";
import { 
  pricingPlans, 
  FEATURE_CATEGORIES, 
  getAdvancedFeatures,
  getPriceId,
  type PlanInterval
} from "./pricing-data";

export default function PricingOptionsTable() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [billingInterval, setBillingInterval] = useState<PlanInterval>("yearly");
  const [openTeamDialog, setOpenTeamDialog] = useState(false);
  const isYearly = billingInterval === "yearly";

  const handleSubscription = async (planId: string) => {
    try {
      setLoadingTier(planId);
      
      if (planId === 'teams') {
        setOpenTeamDialog(true);
        setLoadingTier(null);
        return;
      }

      const priceId = getPriceId(planId, billingInterval);
      
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

  return (
    <div className="w-full">
      <div className="container mx-auto">
        <div className="text-center mb-6 md:mb-8">
          <h2 className="text-4xl md:text-5xl tracking-tighter max-w-xl text-center mx-auto font-regular mb-2 md:mb-3">
            Compare plans & features
          </h2>
          <p className="text-lg leading-relaxed tracking-tight text-muted-foreground max-w-xl text-center mx-auto">
            Choose the right plan for your needs
          </p>
          
          <div className="flex justify-center mt-4 md:mt-8 mb-4 md:mb-6">
            <Tabs 
              defaultValue={billingInterval}
              value={billingInterval}
              onValueChange={(value) => setBillingInterval(value as PlanInterval)}
              className="w-full max-w-[200px]"
            >
              <TabsList className="h-auto gap-2 rounded-none bg-transparent px-0 py-1 text-foreground mb-4 w-full grid grid-cols-2">
                <TabsTrigger
                  value="monthly"
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
                >
                  Monthly
                </TabsTrigger>
                <TabsTrigger
                  value="yearly"
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
                >
                  Yearly
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </div>
          
        <div className="grid text-left w-full grid-cols-4 lg:grid-cols-5 divide-x">
          <div className="col-span-1"></div>
          
          {pricingPlans.map((plan) => (
            <div 
              key={plan.name} 
              className="px-3 py-1 md:px-6 md:py-4 gap-2 flex flex-col justify-between transition-all duration-500"
              style={{ minHeight: "250px" }}
            >
              <div>
                <p className="text-2xl font-medium">{plan.name}</p>
                <p className="text-sm text-muted-foreground h-14">
                  {plan.description}
                </p>
              
                <div className="mt-8">
                  {plan.id === "teams" ? (
                    <p className="text-4xl font-light">Custom</p>
                  ) : (
                    <div className="flex items-baseline">
                      <NumberFlow
                        format={{
                          style: "currency",
                          currency: "USD",
                          minimumFractionDigits: 0,
                          maximumFractionDigits: 0
                        }}
                        value={isYearly ? plan.price.yearly : plan.price.monthly}
                        className="text-4xl font-light transition-all duration-500"
                      />
                      <span className="text-sm text-muted-foreground ml-1">
                        / month
                      </span>
                    </div>
                  )}
                </div>
              </div>
                
                <Button 
                  variant={plan.buttonVariant} 
                  className="gap-2 mt-8"
                  disabled={plan.isCurrent}
                  onClick={() => handleSubscription(plan.id)}
                >
                  {plan.buttonText} 
                  <MoveRight className="w-4 h-4" />
                </Button>
              </div>
            ))}
            
            {/* Render categories and features */}
            {Object.entries(FEATURE_CATEGORIES).map(([category, featureList]) => (
              <React.Fragment key={category}>
                {/* Category header */}
                <div className="px-3 lg:px-6 col-span-1 py-4 mt-8">
                  <p className="text-xs uppercase font-medium tracking-wider">{category}</p>
                </div>
                {pricingPlans.map((plan) => (
                  <div key={`${plan.id}-${category}-header`} className="px-3 py-1 md:px-6 md:py-4 mt-8"></div>
                ))}
                
                {/* Features for this category - no borders at all */}
                {featureList.map((feature) => (
                  <React.Fragment key={feature}>
                    <div className="px-3 lg:px-6 col-span-1 py-4">
                      <div className="flex items-center gap-1">
                        {feature}
                        {feature === "Rent providers API keys" && (
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <InfoIcon className="h-3.5 w-3.5 text-muted-foreground cursor-help ml-1" />
                              </TooltipTrigger>
                              <TooltipContent side="right">
                                <p className="max-w-xs">Use our API keys for third-party services without needing your own accounts</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        )}
                      </div>
                    </div>
                    {pricingPlans.map((plan) => {
                      const planFeature = getAdvancedFeatures(plan, category)
                        .find(f => f.name === feature);
                        
                      return (
                        <div 
                          key={`${plan.id}-${feature}`} 
                          className="px-3 py-1 md:px-6 md:py-4 flex justify-center"
                        >
                          {planFeature ? (
                            typeof planFeature.included === "boolean" ? (
                              planFeature.included ? (
                                <Check className="w-4 h-4 text-primary" />
                              ) : (
                                <Minus className="w-4 h-4 text-muted-foreground" />
                              )
                            ) : (
                              <p className="text-muted-foreground text-sm">{planFeature.included}</p>
                            )
                          ) : (
                            <Minus className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      );
                    })}
                  </React.Fragment>
                ))}
              </React.Fragment>
            ))}
        </div>
      </div>

      <TeamRequestDialog open={openTeamDialog} onOpenChange={setOpenTeamDialog} />
    </div>
  );
}
