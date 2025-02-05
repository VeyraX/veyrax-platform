import type { EndpointData } from "../endpoint-types"

interface ApiProps {
  data: EndpointData
}

export default function Api({ data }: ApiProps) {
  return (
    <div className="w-full">
      <h2 className="text-xl font-bold mb-4">Installation Guide</h2>
      
      <div className="bg-white dark:bg-gray-800 shadow-sm border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-6">
        <p className="mb-3 text-gray-700 dark:text-gray-300">To add this endpoint to your project, run:</p>
        <div className="overflow-x-auto">
          <pre className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 p-3 rounded-md font-mono text-sm">
            npx veyrax@ add {data.path}
          </pre>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="font-semibold mb-3 text-gray-800 dark:text-gray-200">What this will do:</h3>
          <ul className="space-y-2 text-gray-600 dark:text-gray-400">
            <li className="flex items-start">
              <span className="mr-2 mt-1">•</span>
              <div>
                Create components in 
                <code className="mx-1 px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm break-all">
                  src/components/{data.path}
                </code>
              </div>
            </li>
            <li className="flex items-start">
              <span className="mr-2 mt-1">•</span>
              <div className="flex-1">
                Add the following imports:
                <div className="overflow-x-auto mt-2">
                  <pre className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 p-3 rounded-md font-mono text-sm">
                    import {'{'} useEventbrite {'}'} from '@veyrax/eventbrite'
                    import {'{'} EventbriteEvent, EventbriteVenue {'}'} from '@veyrax/types'
                  </pre>
                </div>
              </div>
            </li>
            <li className="flex items-center">
              <span className="mr-2">•</span>
              Configure API integration with pre-built handlers
            </li>
            <li className="flex items-center">
              <span className="mr-2">•</span>
              Add required dependencies to your package.json
            </li>
          </ul>
        </div>

        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg p-4">
          <h3 className="font-semibold mb-3 text-gray-800 dark:text-gray-200">Required API Keys</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-3">
            Add to your <code className="px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded text-sm">.env</code> file:
          </p>
          <div className="overflow-x-auto">
            <pre className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 p-3 rounded-md font-mono text-sm">
              VEYRAX_API_KEY=your_veyrax_api_key_here
              EVENTBRITE_API_KEY=your_eventbrite_api_key_here
            </pre>
          </div>
          <div className="mt-3 text-sm space-y-1">
            <a href="https://www.eventbrite.com/platform/api-keys" className="block text-blue-600 hover:underline">
              • Get Eventbrite API Key
            </a>
            <a href="#" className="block text-blue-600 hover:underline">
              • Get VeyraX API Key
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

