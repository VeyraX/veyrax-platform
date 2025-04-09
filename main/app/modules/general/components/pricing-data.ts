export type PlanInterval = 'monthly' | 'yearly';
export type PlanVariant = 'default' | 'outline' | 'secondary';

export interface PlanFeature {
  name: string;
  included: boolean | string;
  category?: string;
  tooltip?: string;
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

export const pricingPlans: Plan[] = [
  {
    id: "free",
    name: "Free",
    description: "To just get started.",
    price: { monthly: 0, yearly: 0 },
    buttonText: "Current Plan",
    buttonVariant: "outline",
    isCurrent: true,
    features: [
      { name: "5 free tokens", included: true },
      { name: "1,000 API requests / month", included: true },
      { name: "3 projects", included: true },
      { name: "5 free AI generations", included: true },
      { name: "UI Inspirations", included: true },
      
      { name: "API Requests", included: "700 / month", category: "USAGE" },
      { name: "Messages", included: "250", category: "USAGE" },
      { name: "Active Flows", included: "3", category: "USAGE" },
      { name: "Rent providers API keys", included: false, category: "USAGE", tooltip: "Use our API keys for third-party services without needing your own accounts" },
      
      { name: "Premium Components", included: false, category: "FEATURES" },
      { name: "Custom Integrations", included: false, category: "INTEGRATIONS" },
      { name: "Priority", included: "Low", category: "INTEGRATIONS" },
      
      { name: "User Account Auth", included: false, category: "AUTH" },
      { name: "On-premise Deployment", included: false, category: "AUTH" },
      
      { name: "Support Type", included: "Discord", category: "SUPPORT" }
    ]
  },
  {
    id: "starter",
    name: "Starter",
    description: "For higher limits, custom integrations and more flows.",
    price: { monthly: 12, yearly: 8 },
    priceIds: {
      monthly: 'price_1RB5i6IuFYxu6EyPqdW56iPr',
      yearly: 'price_1RArJJIIaSHsQ0m2J30kyQ92'
    },
    buttonText: "Choose Starter",
    buttonVariant: "outline",
    features: [
      { name: "1,500 API requests", included: true },
      { name: "450 Messages", included: true },
      { name: "7 Active Flows", included: true },
      { name: "Rent providers API keys", included: false, tooltip: "Use our API keys for third-party services without needing your own accounts" },
      { name: "Custom integrations", included: true },
      
      { name: "API Requests", included: "1,500 / month", category: "USAGE" },
      { name: "Messages", included: "450", category: "USAGE" },
      { name: "Active Flows", included: "7", category: "USAGE" },
      { name: "Rent providers API keys", included: false, category: "USAGE", tooltip: "Use our API keys for third-party services without needing your own accounts" },
      
      { name: "Custom Integrations", included: true, category: "INTEGRATIONS" },
      { name: "Priority", included: "Medium", category: "INTEGRATIONS" },
      
      { name: "User Account Auth", included: false, category: "AUTH" },
      { name: "On-premise Deployment", included: false, category: "AUTH" },
      
      { name: "Support Type", included: "Discord", category: "SUPPORT" }
    ]
  },
  {
    id: "pro",
    name: "Pro",
    description: "For power users who need bigger limits, integrations, customization and more flows.",
    price: { monthly: 40, yearly: 32 },
    priceIds: {
      monthly: 'price_1RArJwIIaSHsQ0m2tFdvc2xl',
      yearly: 'price_1RBVT8IIaSHsQ0m2TF6Q4Ulw'
    },
    highlight: true,
    buttonText: "Choose Pro",
    buttonVariant: "default",
    features: [
      { name: "3,000 API requests", included: true },
      { name: "950 Messages", included: true },
      { name: "20 Active Flows", included: true },
      { name: "Rent providers API keys", included: true, tooltip: "Use our API keys for third-party services without needing your own accounts" },
      { name: "Custom integrations", included: true },
      
      { name: "API Requests", included: "3,000 / month", category: "USAGE" },
      { name: "Messages", included: "950", category: "USAGE" },
      { name: "Active Flows", included: "20", category: "USAGE" },
      { name: "Rent providers API keys", included: true, category: "USAGE", tooltip: "Use our API keys for third-party services without needing your own accounts" },
      
      { name: "Custom Integrations", included: true, category: "INTEGRATIONS" },
      
      { name: "User Account Auth", included: false, category: "AUTH" },
      { name: "On-premise Deployment", included: false, category: "AUTH" },
      
      { name: "Support Type", included: "Discord + Email", category: "SUPPORT" }
    ]
  },
  {
    id: "teams",
    name: "Teams",
    description: "For businesses who want to offer our tools to their clients.",
    price: { monthly: 0, yearly: 0 },
    buttonText: "Contact Us",
    buttonVariant: "outline",
    features: [
      { name: "Custom API calls", included: true },
      { name: "Custom Flows", included: true },
      { name: "Custom User Auth", included: true },
      { name: "Custom Integrations", included: true },
      { name: "On-premise Deployment", included: true },
      
      { name: "API Requests", included: "Custom", category: "USAGE" },
      { name: "Messages", included: "Custom", category: "USAGE" },
      { name: "Active Flows", included: "Custom", category: "USAGE" },
      { name: "Rent providers API keys", included: false, category: "USAGE", tooltip: "Use our API keys for third-party services without needing your own accounts" },
      
      { name: "Custom Integrations", included: true, category: "INTEGRATIONS" },
      
      { name: "User Account Auth", included: true, category: "AUTH" },
      { name: "On-premise Deployment", included: true, category: "AUTH" },
      
      { name: "Support Type", included: "Discord + WhatsApp", category: "SUPPORT" }
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
    "Custom Integrations"
  ],
  "AUTH": [
    "User Account Auth",
    "On-premise Deployment"
  ],
  "SUPPORT": [
    "Support Type"
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