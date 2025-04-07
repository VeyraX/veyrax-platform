import { Suspense } from "react";
import PricingSuccessPage from "@/app/modules/general/pages/pricing-success-page";

export default function Success() {
  return <Suspense fallback={<div></div>}><PricingSuccessPage /></Suspense>;
}