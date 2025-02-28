"use client"

import { useEffect, useState } from "react"
import { getProviderDetails } from "../api/api.integrations"
import IntegrationDetailSummary from "../components/integration-page-detail/integration-detail-summary"
import IntegrationDetailApiReferences from "../components/integration-page-detail/integration-detail-api-references"
import { ProviderDetails } from "../api/types.integrations"
import { Header } from '@/app/modules/general/components/header'

interface IntegrationPageDetailProps {
  providerTag: string
}

export default function IntegrationPageDetail({ providerTag }: IntegrationPageDetailProps) {
  const [providerDetails, setProviderDetails] = useState<ProviderDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchProviderDetails = async () => {
      if (!providerTag) {
        setError("Invalid provider tag")
        setLoading(false)
        return
      }

      try {
        const details = await getProviderDetails(providerTag)
        setProviderDetails(details)
      } catch (err) {
        console.error('Error fetching provider details:', err)
        setError("Failed to load integration details")
      } finally {
        setLoading(false)
      }
    }

    fetchProviderDetails()
  }, [providerTag])

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      <Header isShowChat={false} />

      <div className="flex-1 px-8 py-6 overflow-auto">
        {loading ? (
          <div className="flex justify-center items-center min-h-[80vh]">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : error || !providerDetails ? (
          <div className="flex justify-center items-center min-h-[80vh] flex-col">
            <h2 className="text-2xl font-bold text-primary mb-4">Error</h2>
            <p className="text-muted-foreground">{error || "Failed to load integration details"}</p>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
            <IntegrationDetailSummary providerDetails={providerDetails} />
            <IntegrationDetailApiReferences providerDetails={providerDetails} />
          </div>
        )}
      </div>
    </div>
  )
}
