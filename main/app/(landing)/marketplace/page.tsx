'use client'
import IntegrationsPage from "@/app/modules/integrations/pages/integrations-page";
import { Footer } from "@/app/modules/landing/components/footer";

export default function MarketplacePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <IntegrationsPage isPublic={true} />
      <Footer />
    </div>
  );
}
