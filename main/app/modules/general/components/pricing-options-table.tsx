"use client";

import * as React from "react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs-updated";
import { Check, Minus, MoveRight, PhoneCall } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import NumberFlow from "@number-flow/react";
import { 
  pricingPlans, 
  FEATURE_CATEGORIES, 
  getAdvancedFeatures,
  type PlanInterval
} from "./pricing-data";

export default function PricingOptionsTable() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [billingInterval, setBillingInterval] = useState<PlanInterval>("yearly");
  const isYearly = billingInterval === "yearly";

  const handleSubscription = (planId: string) => {
    setLoadingTier(planId);
    setTimeout(() => {
      setLoadingTier(null);
      toast.success(`Successfully subscribed to ${planId} plan!`);
    }, 1500);
  };

  return (
    <div className="w-full">
      <div className="container mx-auto">
        <div className="flex text-center justify-center items-center gap-4 flex-col">
          <div className="flex gap-2 flex-col">
            <h2 className="text-3xl md:text-5xl tracking-tighter max-w-xl text-center font-regular">
              Compare plans & features
            </h2>
            <p className="text-lg leading-relaxed tracking-tight text-muted-foreground max-w-xl text-center">
              Choose the right plan for your needs and budget
            </p>
          </div>
          
          <div className="flex justify-center mt-8 mb-8">
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
          
          <div className="grid text-left w-full grid-cols-4 lg:grid-cols-5 divide-x pt-20">
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
                      <p className="text-4xl font-bold">Custom</p>
                    ) : (
                      <div className="flex items-baseline">
                        <NumberFlow
                          format={{
                            style: "currency",
                            currency: "USD",
                            trailingZeroDisplay: "stripIfInteger",
                          }}
                          value={isYearly ? plan.price.yearly : plan.price.monthly}
                          className="text-4xl font-bold transition-all duration-500"
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
                  {plan.id === "teams" ? 
                    <PhoneCall className="w-4 h-4" /> : 
                    <MoveRight className="w-4 h-4" />
                  }
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
                      {feature}
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
      </div>
    </div>
  );
}
