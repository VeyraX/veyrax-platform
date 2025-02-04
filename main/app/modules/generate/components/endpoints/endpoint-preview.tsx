import React from 'react'
import type { EndpointData } from "../../endpoint-types"

interface PreviewProps {
  data: EndpointData
}

export default function Preview({ data }: PreviewProps) {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-2">Preview</h2>
      {data.preview}
    </div>
  )
}

