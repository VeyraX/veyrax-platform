'use client'
import IntegrationPageDetail from "@/app/modules/integrations/pages/integration-page-detail"
import { Footer } from "@/app/modules/landing/components/footer"

interface IntegrationDetailPageProps {
  params: {
    provider_tag: string
  }
}

export default function IntegrationDetail({ params }: IntegrationDetailPageProps) {
  return (
    <div className="flex flex-col min-h-screen">
      <IntegrationPageDetail providerTag={params.provider_tag} isPublic={true} />
      <Footer />
    </div>
  )
}