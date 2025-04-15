'use client'
import IntegrationsMainPage from "@/app/modules/integrations/pages/integrations-main-page";
import { Footer } from "@/app/modules/landing/components/footer";

export default function MarketplacePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <IntegrationsMainPage isPublic={true} />
      <Footer />
    </div>
  );
}
