"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import PricingOptions from "../components/pricing-options";
import PricingOptionsTable from "../components/pricing-options-table";

export default function PricingPage() {
    const searchParams = useSearchParams();
    const canceled = searchParams.get("canceled");
    
    useEffect(() => {
        if (canceled) {
            toast.error("Payment was canceled. Please try again when you're ready.");
        }
    }, [canceled]);
    
    return (
        <div className="flex flex-col gap-8">
            <PricingOptions />
            <div className="hidden lg:block">
                <PricingOptionsTable />
            </div>
        </div>
    );
}