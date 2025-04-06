"use client";

import * as React from "react";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs-updated";
import { Check, Minus, MoveRight, PhoneCall } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import NumberFlow from "@number-flow/react";

// Определяем категории функций
const FEATURE_CATEGORIES = {
  "USAGE": [
    "Monthly Tokens",
    "API Requests",
    "Projects"
  ],
  "FEATURES": [
    "Premium Components",
    "Custom Integrations",
    "White Labeling"
  ],
  "AI TOOLS": [
    "AI Component Generation",
    "UI Inspirations",
    "Code Generation"
  ],
  "SUPPORT": [
    "Response Time",
    "Priority Support",
    "Dedicated Manager"
  ]
};

interface Plan {
  name: string;
  description: string;
  price: { monthly: number; yearly: number };
  tokenCount: { monthly: string; yearly: string };
  tokenRate?: { monthly: string; yearly: string };
  buttonText: string;
  buttonAction: () => void;
  buttonVariant: "default" | "outline" | "secondary";
  features: Record<string, string | boolean>;
  isCurrent?: boolean;
}

export default function PricingOptionsTable() {
  const [loadingTier, setLoadingTier] = useState<string | null>(null);
  const [billingInterval, setBillingInterval] = useState<"monthly" | "yearly">("yearly");
  const isYearly = billingInterval === "yearly";

  const handleSubscription = (packageName: string) => {
    setLoadingTier(packageName);
    setTimeout(() => {
      setLoadingTier(null);
      toast.success(`Successfully subscribed to ${packageName} plan!`);
    }, 1500);
  };

  const plans: Plan[] = [
    {
      name: "Free",
      description: "For personal use, small projects, and testing the platform",
      price: { monthly: 0, yearly: 0 },
      tokenCount: { 
        monthly: "5 tokens included", 
        yearly: "5 tokens included" 
      },
      buttonText: "Current Plan",
      buttonAction: () => {},
      buttonVariant: "outline",
      isCurrent: true,
      features: {
        // Usage
        "Monthly Tokens": "5 free tokens",
        "API Requests": "1,000 / month",
        "Projects": "3 projects",
        
        // Features
        "Premium Components": false,
        "Custom Integrations": false,
        "White Labeling": false,
        
        // AI Tools
        "AI Component Generation": "5 free generation",
        "UI Inspirations": true,
        "Code Generation": false,
        
        // Support
        "Response Time": "48 hours",
        "Priority Support": false,
        "Dedicated Manager": false
      }
    },
    {
      name: "Pro",
      description: "For professionals who need more tokens and premium features",
      price: { monthly: 10, yearly: 8 },
      tokenCount: { 
        monthly: "50 tokens included", 
        yearly: "50 tokens included" 
      },
      tokenRate: { 
        monthly: "($0.20/token)", 
        yearly: "($0.16/token)" 
      },
      buttonText: "Upgrade",
      buttonAction: () => handleSubscription("Pro"),
      buttonVariant: "default",
      features: {
        // Usage
        "Monthly Tokens": "50 tokens",
        "API Requests": "10,000 / month",
        "Projects": "10 projects",
        
        // Features
        "Premium Components": true,
        "Custom Integrations": false,
        "White Labeling": false,
        
        // AI Tools
        "AI Component Generation": true,
        "UI Inspirations": true,
        "Code Generation": true,
        
        // Support
        "Response Time": "24 hours",
        "Priority Support": false,
        "Dedicated Manager": false
      }
    },
    {
      name: "Pro Plus",
      description: "For power users and small teams needing more resources",
      price: { monthly: 29, yearly: 24 },
      tokenCount: { 
        monthly: "200 tokens included", 
        yearly: "200 tokens included" 
      },
      tokenRate: { 
        monthly: "($0.15/token)", 
        yearly: "($0.12/token)" 
      },
      buttonText: "Upgrade",
      buttonAction: () => handleSubscription("Pro Plus"),
      buttonVariant: "outline",
      features: {
        // Usage
        "Monthly Tokens": "200 tokens",
        "API Requests": "50,000 / month",
        "Projects": "Unlimited",
        
        // Features
        "Premium Components": true,
        "Custom Integrations": true,
        "White Labeling": false,
        
        // AI Tools
        "AI Component Generation": true,
        "UI Inspirations": true,
        "Code Generation": true,
        
        // Support
        "Response Time": "12 hours",
        "Priority Support": true,
        "Dedicated Manager": false
      }
    },
    {
      name: "Enterprise",
      description: "For organizations needing custom solutions and support",
      price: { monthly: 120, yearly: 99 },
      tokenCount: { 
        monthly: "1000 tokens included", 
        yearly: "1000 tokens included" 
      },
      tokenRate: { 
        monthly: "($0.12/token)", 
        yearly: "($0.10/token)" 
      },
      buttonText: "Contact Sales",
      buttonAction: () => handleSubscription("Enterprise"),
      buttonVariant: "outline",
      features: {
        // Usage
        "Monthly Tokens": "1000 tokens",
        "API Requests": "Unlimited",
        "Projects": "Unlimited",
        
        // Features
        "Premium Components": true,
        "Custom Integrations": true,
        "White Labeling": true,
        
        // AI Tools
        "AI Component Generation": true,
        "UI Inspirations": true,
        "Code Generation": true,
        
        // Support
        "Response Time": "4 hours",
        "Priority Support": true,
        "Dedicated Manager": true
      }
    }
  ];

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
              onValueChange={(value) => setBillingInterval(value as "monthly" | "yearly")}
              className="w-full max-w-[240px]"
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
            
            {plans.map((plan) => (
              <div 
                key={plan.name} 
                className="px-3 py-1 md:px-6 md:py-4 gap-2 flex flex-col transition-all duration-500"
              >
                <p className="text-2xl">{plan.name}</p>
                <p className="text-sm text-muted-foreground">
                  {plan.description}
                </p>
                <div className="flex flex-col lg:flex-row lg:items-center gap-2 text-xl mt-8">
                  <NumberFlow
                    format={{
                      style: "currency",
                      currency: "USD",
                      trailingZeroDisplay: "stripIfInteger",
                    }}
                    value={isYearly ? plan.price.yearly : plan.price.monthly}
                    className="text-4xl font-bold"
                  />
                  <span className="text-sm text-muted-foreground">
                    / month {isYearly && "(billed yearly)"}
                  </span>
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {isYearly ? plan.tokenCount.yearly : plan.tokenCount.monthly}
                  {plan.tokenRate && <span> {isYearly ? plan.tokenRate.yearly : plan.tokenRate.monthly}</span>}
                </div>
                <Button 
                  variant={plan.name === "Pro" ? "default" : "outline"} 
                  className="gap-4 mt-8"
                  disabled={plan.isCurrent}
                  onClick={plan.buttonAction}
                >
                  {plan.buttonText} 
                  {plan.name === "Enterprise" ? 
                    <PhoneCall className="w-4 h-4" /> : 
                    <MoveRight className="w-4 h-4" />
                  }
                </Button>
              </div>
            ))}
            
            {/* Render categories and features */}
            {Object.entries(FEATURE_CATEGORIES).map(([category, featureList], categoryIndex) => (
              <React.Fragment key={category}>
                {/* Category header */}
                <div className="px-3 lg:px-6 col-span-1 py-4 mt-8">
                  <p className="text-xs uppercase font-medium tracking-wider">{category}</p>
                </div>
                {plans.map((plan) => (
                  <div key={`${plan.name}-${category}-header`} className="px-3 py-1 md:px-6 md:py-4 mt-8"></div>
                ))}
                
                {/* Features for this category - no borders at all */}
                {featureList.map((feature) => (
                  <React.Fragment key={feature}>
                    <div className="px-3 lg:px-6 col-span-1 py-4">
                      {feature}
                    </div>
                    {plans.map((plan) => (
                      <div 
                        key={`${plan.name}-${feature}`} 
                        className="px-3 py-1 md:px-6 md:py-4 flex justify-center"
                      >
                        {typeof plan.features[feature] === "boolean" ? (
                          plan.features[feature] ? (
                            <Check className="w-4 h-4 text-primary" />
                          ) : (
                            <Minus className="w-4 h-4 text-muted-foreground" />
                          )
                        ) : (
                          <p className="text-muted-foreground text-sm">{plan.features[feature]}</p>
                        )}
                      </div>
                    ))}
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
