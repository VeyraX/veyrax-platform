import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  PlusIcon, 
  GlobeIcon, 
  ArrowUpRightIcon, 
  TargetIcon, 
  SettingsIcon 
} from "lucide-react"
import { IntegrationDetailSummaryProps } from "../../api/types.integrations"

export default function IntegrationDetailSummary({ providerDetails }: IntegrationDetailSummaryProps) {
  const { provider, totalEndpoints, totalParameters, totalComponents, endpointsList } = providerDetails

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start mb-6">
          <div className="flex items-start gap-4">
            {provider.logo_url && (
              <div className="w-12 h-12 flex-shrink-0 rounded-lg overflow-hidden">
                <img 
                  src={provider.logo_url} 
                  alt={`${provider.name} logo`} 
                  className="w-full h-full object-contain"
                />
              </div>
            )}
            <div>
              <h1 className="text-3xl font-bold text-foreground mb-2">{provider.name}</h1>
              <p className="text-muted-foreground mt-4">{provider.description}</p>
            </div>
          </div>
          <Button className="mt-4 md:mt-0">
            <PlusIcon size={16} />
            Connect
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <ArrowUpRightIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalEndpoints}</h2>
                <p className="text-muted-foreground">Total Endpoints</p>
              </div>
            </div>
          </div>
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <TargetIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalParameters}</h2>
                <p className="text-muted-foreground">Total Parameters</p>
              </div>
            </div>
          </div>
          <div className="border border-border rounded-lg p-6 bg-card">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-muted rounded-md">
                <SettingsIcon size={18} className="text-foreground" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-foreground">{totalComponents}</h2>
                <p className="text-muted-foreground">UI Components</p>
              </div>
            </div>
          </div>
        </div>

        <div className="border border-border rounded-lg p-6 mb-8 bg-card">
          <h2 className="text-lg font-bold mb-1 text-foreground">Available Endpoints</h2>
          <p className="text-muted-foreground mb-6">
            Contains {totalEndpoints} endpoints that agents can invoke with natural language.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-muted-foreground">
                  <th className="pb-4 font-medium w-1/4">Endpoint</th>
                  <th className="pb-4 font-medium w-2/5">Description</th>
                  <th className="pb-4 font-medium text-center w-1/6">Parameters</th>
                </tr>
              </thead>
              <tbody>
                {endpointsList.map((endpoint, index) => (
                  <tr key={index} className="border-t border-border">
                    <td className="py-4 pr-4">
                      <div className="font-medium text-foreground">{endpoint.name}</div>
                      <div className="text-sm text-muted-foreground">{endpoint.functionId}</div>
                    </td>
                    <td className="py-4 pr-4 text-muted-foreground">
                      {endpoint.description}
                    </td>
                    <td className="py-4 text-center text-muted-foreground">{endpoint.paramCount}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}

