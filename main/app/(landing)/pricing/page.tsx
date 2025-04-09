import PricingPage from "@/app/modules/general/pages/pricing-page";
import { Suspense } from "react";

export default function Pricing() {
  return (
    <Suspense fallback={<div></div>}>
      <PricingPage />
    </Suspense>
  );
}