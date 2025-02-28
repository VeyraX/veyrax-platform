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

  // Форматирование даты создания
  const formatCreatedDate = () => {
    if (!provider.created_at) return "N/A"
    
    try {
      // Если это timestamp в секундах
      const timestamp = typeof provider.created_at === 'string' 
        ? parseInt(provider.created_at) 
        : provider.created_at
        
      const date = new Date(timestamp * 1000)
      return date.toLocaleDateString('en-US', {
        month: 'numeric',
        day: 'numeric',
        year: 'numeric'
      })
    } catch (e) {
      console.error('Error formatting date:', e)
      return "N/A"
    }
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
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
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{provider.name}</h1>
              <p className="text-gray-700 mt-4">{provider.description}</p>
            </div>
          </div>
          <Button className="mt-4 md:mt-0 bg-gray-900 hover:bg-gray-800">
            <PlusIcon size={16} />
            Connect
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-gray-50 rounded-md">
                <ArrowUpRightIcon size={18} />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{totalEndpoints}</h2>
                <p className="text-gray-600">Total Endpoints</p>
              </div>
            </div>
          </div>
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-gray-50 rounded-md">
                <TargetIcon size={18} />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{totalParameters}</h2>
                <p className="text-gray-600">Total Parameters</p>
              </div>
            </div>
          </div>
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <div className="p-2 bg-gray-50 rounded-md">
                <SettingsIcon size={18} />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{totalComponents}</h2>
                <p className="text-gray-600">UI Components</p>
              </div>
            </div>
          </div>
        </div>

        <div className="border border-gray-200 rounded-lg p-6 mb-8">
          <h2 className="text-lg font-bold mb-1">Available Endpoints</h2>
          <p className="text-gray-600 mb-6">
            Contains {totalEndpoints} endpoints that agents can invoke with natural language.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-600">
                  <th className="pb-4 font-medium w-1/4">Endpoint</th>
                  <th className="pb-4 font-medium w-2/5">Description</th>
                  <th className="pb-4 font-medium text-center w-1/6">Parameters</th>
                </tr>
              </thead>
              <tbody>
                {endpointsList.map((endpoint, index) => (
                  <tr key={index} className="border-t border-gray-200">
                    <td className="py-4 pr-4">
                      <div className="font-medium">{endpoint.name}</div>
                      <div className="text-sm text-gray-500">{endpoint.functionId}</div>
                    </td>
                    <td className="py-4 pr-4 text-gray-700">
                      {endpoint.description}
                    </td>
                    <td className="py-4 text-center">{endpoint.paramCount}</td>
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

