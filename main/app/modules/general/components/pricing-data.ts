export type PlanInterval = 'monthly' | 'yearly';
export type PlanVariant = 'default' | 'outline' | 'secondary';

export interface PlanFeature {
  name: string;
  included: boolean | string;
  category?: string;
}

export interface Plan {
  id: string;
  name: string;
  description: string;
  price: {
    monthly: number;
    yearly: number;
  };
  tokenCount?: {
    monthly: string;
    yearly: string;
  };
  tokenRate?: {
    monthly: string;
    yearly: string;
  };
  priceIds?: {
    monthly: string;
    yearly: string;
  };
  highlight?: boolean;
  isCurrent?: boolean;
  buttonText: string;
  buttonVariant?: PlanVariant;
  features: PlanFeature[];
}

// Unified plan data that combines both pricing tables
export const pricingPlans: Plan[] = [
  {
    id: "free",
    name: "Free",
    description: "For personal use, small projects, and testing the platform",
    price: { monthly: 0, yearly: 0 },
    tokenCount: { 
      monthly: "5 tokens included", 
      yearly: "5 tokens included" 
    },
    buttonText: "Current Plan",
    buttonVariant: "outline",
    isCurrent: true,
    features: [
      // Simple view features
      { name: "5 free tokens", included: true },
      { name: "1,000 API requests / month", included: true },
      { name: "3 projects", included: true },
      { name: "5 free AI generations", included: true },
      { name: "UI Inspirations", included: true },
      
      // Advanced view features - with categories
      { name: "API Requests", included: "1,000 / month", category: "USAGE" },
      { name: "Messages", included: "Limited", category: "USAGE" },
      { name: "Active Flows", included: "3", category: "USAGE" },
      { name: "Rent providers API keys", included: false, category: "USAGE" },
      
      { name: "Premium Components", included: false, category: "FEATURES" },
      { name: "Custom Integrations", included: false, category: "INTEGRATIONS" },
      { name: "Priority", included: "Low", category: "INTEGRATIONS" },
      
      { name: "User account Auth", included: false, category: "AUTH" },
      { name: "On-premise", included: false, category: "AUTH" },
      
      { name: "Support", included: "Discord", category: "SUPPORT" },
      { name: "Priority Support", included: false, category: "SUPPORT" },
      { name: "Dedicated Manager", included: false, category: "SUPPORT" }
    ]
  },
  {
    id: "starter",
    name: "Starter",
    description: "Just to get started",
    price: { monthly: 12, yearly: 8 },
    tokenCount: { 
      monthly: "50 tokens included", 
      yearly: "50 tokens included" 
    },
    tokenRate: { 
      monthly: "($0.24/token)", 
      yearly: "($0.16/token)" 
    },
    priceIds: {
      monthly: 'price_1OxVblD7STfJJkPfuQFD58qG',
      yearly: 'price_1OxYOuD7STfJJkPf3VzpHGQx'
    },
    buttonText: "Choose Starter",
    buttonVariant: "outline",
    features: [
      // Simple view features
      { name: "600 API requests", included: true },
      { name: "Unlimited Messages", included: true },
      { name: "10 Active Flows", included: true },
      { name: "Rent providers API keys", included: false },
      { name: "Custom integrations", included: false },
      
      // Advanced view features - with categories
      { name: "API Requests", included: "600 / month", category: "USAGE" },
      { name: "Messages", included: "Unlimited", category: "USAGE" },
      { name: "Active Flows", included: "10", category: "USAGE" },
      { name: "Rent providers API keys", included: false, category: "USAGE" },
      
      { name: "Premium Components", included: true, category: "FEATURES" },
      { name: "Custom Integrations", included: false, category: "INTEGRATIONS" },
      { name: "Priority", included: "Medium", category: "INTEGRATIONS" },
      
      { name: "User account Auth", included: false, category: "AUTH" },
      { name: "On-premise", included: false, category: "AUTH" },
      
      { name: "Support", included: "Discord", category: "SUPPORT" },
      { name: "Priority Support", included: false, category: "SUPPORT" },
      { name: "Dedicated Manager", included: false, category: "SUPPORT" }
    ]
  },
  {
    id: "pro",
    name: "Pro",
    description: "For professionals who need more tokens and premium features",
    price: { monthly: 40, yearly: 32 },
    tokenCount: { 
      monthly: "200 tokens included", 
      yearly: "200 tokens included" 
    },
    tokenRate: { 
      monthly: "($0.20/token)", 
      yearly: "($0.16/token)" 
    },
    priceIds: {
      monthly: 'price_1RB5i6IuFYxu6EyPqdW56iPr',
      yearly: 'price_1RB5mUIuFYxu6EyPb2Oxmsck'
    },
    highlight: true,
    buttonText: "Choose Pro",
    buttonVariant: "default",
    features: [
      { name: "1,500 API requests", included: true },
      { name: "Unlimited Messages", included: true },
      { name: "30 Active Flows", included: true },
      { name: "Rent providers API keys", included: true },
      { name: "Custom integrations", included: true },
      
      { name: "API Requests", included: "1,500 / month", category: "USAGE" },
      { name: "Messages", included: "Unlimited", category: "USAGE" },
      { name: "Active Flows", included: "30", category: "USAGE" },
      { name: "Rent providers API keys", included: true, category: "USAGE" },
      
      { name: "Premium Components", included: true, category: "FEATURES" },
      { name: "Custom Integrations", included: true, category: "INTEGRATIONS" },
      { name: "Priority", included: "High", category: "INTEGRATIONS" },
      
      { name: "User account Auth", included: false, category: "AUTH" },
      { name: "On-premise", included: false, category: "AUTH" },
      
      { name: "Support", included: "Separate Discord Channel", category: "SUPPORT" },
      { name: "Priority Support", included: true, category: "SUPPORT" },
      { name: "Dedicated Manager", included: false, category: "SUPPORT" }
    ]
  },
  {
    id: "teams",
    name: "Teams",
    description: "For production Agents who need tools and customization",
    price: { monthly: 0, yearly: 0 },
    buttonText: "Contact Sales",
    buttonVariant: "outline",
    features: [
      { name: "Custom API calls", included: true },
      { name: "Custom flows", included: true },
      { name: "Custom branding", included: true },
      { name: "Dedicated account manager", included: true },
      
      { name: "API Requests", included: "Custom", category: "USAGE" },
      { name: "Messages", included: "Unlimited", category: "USAGE" },
      { name: "Active Flows", included: "Unlimited", category: "USAGE" },
      { name: "Rent providers API keys", included: true, category: "USAGE" },
      
      { name: "Premium Components", included: true, category: "FEATURES" },
      { name: "Custom Integrations", included: true, category: "INTEGRATIONS" },
      { name: "Priority", included: "Highest", category: "INTEGRATIONS" },
      
      { name: "User account Auth", included: true, category: "AUTH" },
      { name: "On-premise", included: true, category: "AUTH" },
      
      { name: "Support", included: "Separate Discord Channel and WhatsApp", category: "SUPPORT" }
    ]
  }
];


export const FEATURE_CATEGORIES = {
  "USAGE": [
    "API Requests",
    "Messages",
    "Active Flows",
    "Rent providers API keys"
  ],
  "INTEGRATIONS": [
    "Custom Integrations",
    "Priority"
  ],
  "AUTH": [
    "User account Auth",
    "On-premise"
  ],
  "SUPPORT": [
    "Support",
    "Priority Support",
    "Dedicated Manager"
  ]
};


export function getSimpleFeatures(plan: Plan): PlanFeature[] {
  return plan.features.filter(feature => !feature.category);
}

export function getAdvancedFeatures(plan: Plan, category: string): PlanFeature[] {
  return plan.features.filter(feature => feature.category === category);
}

export function getPlanById(id: string): Plan | undefined {
  return pricingPlans.find(plan => plan.id === id);
}

export function getPriceId(planId: string, interval: PlanInterval): string | undefined {
  const plan = getPlanById(planId);
  return plan?.priceIds?.[interval];
} 