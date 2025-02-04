import type { EndpointData } from "../../endpoint-types"

interface ApiProps {
  data: EndpointData
}

export default function Api({ data }: ApiProps) {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">{data.method}</h2>
      <p className="mb-2">
        <strong>Description:</strong> {data.description}
      </p>
      <h3 className="text-md font-semibold mt-4 mb-2">Input Schema</h3>
      <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded">{JSON.stringify(data.inputSchema, null, 2)}</pre>
      <h3 className="text-md font-semibold mt-4 mb-2">Response Schema</h3>
      <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded">{JSON.stringify(data.responseSchema, null, 2)}</pre>
    </div>
  )
}

