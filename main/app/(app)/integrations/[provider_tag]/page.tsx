import IntegrationPageDetail from "@/app/modules/integrations/pages/integration-page-detail"

interface IntegrationDetailPageProps {
  params: {
    provider_tag: string
  }
}

export default function IntegrationDetail({ params }: IntegrationDetailPageProps) {
  return <IntegrationPageDetail providerTag={params.provider_tag} />
}