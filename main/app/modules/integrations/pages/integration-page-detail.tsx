"use client"

import { useEffect, useState } from "react"
import { getProviderDetails } from "../api/api.integrations"
import IntegrationDetailSummary from "../components/integration-page-detail/integration-detail-summary"
import IntegrationDetailApiReferences from "../components/integration-page-detail/integration-detail-api-references"
import { ProviderDetails } from "../api/types.integrations"
import { Header } from '@/app/modules/general/components/header'
import { Skeleton } from "@/components/ui/skeleton"

interface IntegrationPageDetailProps {
  providerTag: string
  isPublic?: boolean
}

export default function IntegrationPageDetail({ providerTag, isPublic = false }: IntegrationPageDetailProps) {
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

  const renderSkeleton = () => {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start mb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 flex-shrink-0 rounded-lg overflow-hidden">
              <Skeleton className="w-full h-full" />
            </div>
            <div>
              <Skeleton className="h-8 w-64 mb-2" />
              <Skeleton className="h-4 w-full max-w-md mt-4" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-border rounded-lg p-6 bg-card">
              <div className="flex items-start gap-3">
                <Skeleton className="h-10 w-10 rounded-md" />
                <div>
                  <Skeleton className="h-8 w-16 mb-2" />
                  <Skeleton className="h-4 w-24" />
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="border border-border rounded-lg p-6 mb-8 bg-card">
          <Skeleton className="h-6 w-48 mb-1" />
          <Skeleton className="h-4 w-full max-w-md mb-6" />

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left">
                  <th className="pb-4 w-1/4"><Skeleton className="h-4 w-20" /></th>
                  <th className="pb-4 w-2/5"><Skeleton className="h-4 w-24" /></th>
                  <th className="pb-4 text-center w-1/6"><Skeleton className="h-4 w-16 mx-auto" /></th>
                  <th className="pb-4 text-right w-1/6"></th>
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4, 5].map((i) => (
                  <tr key={i} className="border-t border-border">
                    <td className="py-4 pr-4">
                      <Skeleton className="h-5 w-32 mb-1" />
                      <Skeleton className="h-3 w-24" />
                    </td>
                    <td className="py-4 pr-4">
                      <Skeleton className="h-4 w-full" />
                    </td>
                    <td className="py-4 text-center">
                      <Skeleton className="h-4 w-8 mx-auto" />
                    </td>
                    <td className="py-4 text-right">
                      <Skeleton className="h-6 w-6 ml-auto rounded-full" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col relative h-[100vh] w-full">
      {!isPublic && <Header isShowChat={false} />}

      <div className="flex-1 px-8 py-6 overflow-auto">
        {loading ? (
          renderSkeleton()
        ) : error || !providerDetails ? (
          <div className="flex justify-center items-center min-h-[80vh] flex-col">
            <h2 className="text-2xl font-bold text-primary mb-4">Error</h2>
            <p className="text-muted-foreground">{error || "Failed to load integration details"}</p>
          </div>
        ) : (
          <div className="max-w-6xl mx-auto">
            <IntegrationDetailSummary providerDetails={providerDetails} isPublic={isPublic} />
            <IntegrationDetailApiReferences providerDetails={providerDetails} />
          </div>
        )}
      </div>
    </div>
  )
}
