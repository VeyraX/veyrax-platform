'use client';

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { CreditCard, ExternalLink, BarChart4 } from "lucide-react";
import { useState, useEffect } from "react";
import { format } from "date-fns";
import { UserSubscription, ProductInfo, UserUsage } from "../api/types.settings";
import { getUserUsage, getUserProductInfo } from "../api/api.settings";
import { Progress } from "@/components/ui/progress";

interface BillingSettingsProps {
  subscriptionInfo: UserSubscription | null;
  isLoading: boolean;
}

export default function BillingSettings({ subscriptionInfo, isLoading }: BillingSettingsProps) {
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [usage, setUsage] = useState<UserUsage | null>(null);
  const [productInfo, setProductInfo] = useState<ProductInfo | null>(null);
  const [isLoadingUsage, setIsLoadingUsage] = useState(true);

  useEffect(() => {
    const fetchUsageData = async () => {
      setIsLoadingUsage(true);
      try {
        const [usageData, productData] = await Promise.all([
          getUserUsage(),
          getUserProductInfo()
        ]);
        setUsage(usageData);
        setProductInfo(productData);
      } catch (error) {
        console.error('Error fetching usage data:', error);
      } finally {
        setIsLoadingUsage(false);
      }
    };

    fetchUsageData();
  }, []);

  const handleCustomerPortal = async () => {
    try {
      setIsRedirecting(true);
      const response = await fetch('/api/stripe/customer-portal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error('Failed to create customer portal session');
      }

      const { url } = await response.json();
      window.location.href = url;
    } catch (error) {
      console.error('Error redirecting to customer portal:', error);
      setIsRedirecting(false);
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency || 'USD',
    }).format(amount / 100); // Stripe amounts are in cents
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'past_due':
        return 'bg-yellow-100 text-yellow-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      case 'unpaid':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Calculates the percentage of usage against limit
  const calculatePercentage = (used: number, limit: number | string): number => {
    if (typeof limit === 'string') {
      if (limit === 'unlimited' || limit === 'custom') return 0;
      return 0;
    }
    return Math.min(Math.round((used / limit) * 100), 100);
  };

  const formatLimit = (limit: number | string): string => {
    if (limit === undefined || limit === null) {
      return 'N/A';
    }
    
    if (typeof limit === 'string') {
      return limit.charAt(0).toUpperCase() + limit.slice(1);
    }
    return limit.toLocaleString();
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Billing</h2>
          <p className="text-sm text-muted-foreground">Manage your subscription and payment details.</p>
        </div>
        
        <Separator />

        <div className="space-y-4">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-10 w-40" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Billing</h2>
        <p className="text-sm text-muted-foreground">Manage your subscription and payment details.</p>
      </div>

      <Separator />

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Subscription</h3>
        </div>
        
        {subscriptionInfo ? (
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-1">
              <span className="text-sm text-muted-foreground">Plan</span>
              <p className="font-medium">{subscriptionInfo.product_name}</p>
            </div>
            
            <div className="space-y-1">
              <span className="text-sm text-muted-foreground">Status</span>
              <p>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusBadgeColor(subscriptionInfo.is_canceled ? 'canceled' : subscriptionInfo.subscription_status)}`}>
                  {subscriptionInfo.is_canceled 
                    ? "Canceled" 
                    : subscriptionInfo.subscription_status.charAt(0).toUpperCase() + subscriptionInfo.subscription_status.slice(1)}
                </span>
              </p>
            </div>
            
            <div className="space-y-1">
              <span className="text-sm text-muted-foreground">Amount</span>
              <p className="font-medium">{subscriptionInfo.amount_usd} USD</p>
            </div>
            
            <div className="space-y-1">
              <span className="text-sm text-muted-foreground">
                {subscriptionInfo.canceled_at ? "Active Until" : "Next billing date"}
              </span>
              <p className="font-medium">
                {subscriptionInfo.subscription_end_date ? format(new Date(subscriptionInfo.subscription_end_date), 'MMMM d, yyyy') : 'N/A'}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex justify-between items-center">
            <div className="space-y-1">
              <span className="text-sm text-muted-foreground">Plan</span>
              <p className="font-medium">{productInfo?.name || 'Free'}</p>
            </div>
            <Button 
              onClick={() => window.location.href = '/pricing'} 
              className="self-end"
            >
              Upgrade Plan
            </Button>
          </div>
        )}
        
        <div className="pt-4">
          {subscriptionInfo && (
            <Button 
              onClick={handleCustomerPortal} 
              disabled={isRedirecting}
              className="w-full sm:w-auto"
            >
              {isRedirecting 
                ? 'Redirecting...' 
                : subscriptionInfo.is_canceled 
                  ? 'Restore Subscription'
                  : 'Manage Subscription'
              }
            </Button>
          )}
        </div>
      </div>
      
      <Separator />
      
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Usage</h3>
        </div>
        
        {isLoadingUsage ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-16" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-16" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-1/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-16" />
            </div>
          </div>
        ) : usage && productInfo?.attrs ? (
          <div className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>API Requests</span>
                <span>{usage.api_call_count} / {formatLimit(productInfo.attrs.api_call_count)}</span>
              </div>
              <Progress 
                value={calculatePercentage(usage.api_call_count, productInfo.attrs.api_call_count)} 
                className="h-2" 
              />
              <p className="text-xs text-muted-foreground">
                {typeof productInfo.attrs.api_call_count === 'string' 
                  ? 'No fixed limit on API requests'
                  : `${usage.api_call_count} of ${productInfo.attrs.api_call_count} API requests used this month`
                }
              </p>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Messages</span>
                <span>{usage.message_count} / {formatLimit(productInfo.attrs.message_count)}</span>
              </div>
              <Progress 
                value={calculatePercentage(usage.message_count, productInfo.attrs.message_count)} 
                className="h-2" 
              />
              <p className="text-xs text-muted-foreground">
                {typeof productInfo.attrs.message_count === 'string' 
                  ? 'No fixed limit on messages'
                  : `${usage.message_count} of ${productInfo.attrs.message_count} messages used this month`
                }
              </p>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Active Flows</span>
                <span>{usage.active_flow_count} / {formatLimit(productInfo.attrs.active_flow_count)}</span>
              </div>
              <Progress 
                value={calculatePercentage(usage.active_flow_count, productInfo.attrs.active_flow_count)} 
                className="h-2" 
              />
              <p className="text-xs text-muted-foreground">
                {typeof productInfo.attrs.active_flow_count === 'string' 
                  ? 'No fixed limit on flows'
                  : `${usage.active_flow_count} of ${productInfo.attrs.active_flow_count} flows used`
                }
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center py-4 text-muted-foreground">
            Unable to load usage data.
          </div>
        )}
      </div>
    </div>
  );
} 