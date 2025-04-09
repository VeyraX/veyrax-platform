"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import PricingOptions from "../components/pricing-options";
import PricingOptionsTable from "../components/pricing-options-table";
import { FaqSectionDemo } from "../components/pricing-faq";
import { Footer } from "@/app/modules/landing/components/footer";
export default function PricingPage() {
    const searchParams = useSearchParams();
    
    return (
        <div className="flex flex-col gap-12 md:gap-24 pt-12 md:pt-24">
            <div className="py-4 md:py-8">
                <PricingOptions />
            </div>
            <div className="hidden lg:block py-4 md:py-8">
                <PricingOptionsTable />
            </div>
            <div className="py-4 md:py-8">
                <FaqSectionDemo />
            </div>
            <div className="py-4 md:py-8">
                <Footer />
            </div>
        </div>
    );
}