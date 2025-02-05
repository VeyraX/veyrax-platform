import React from 'react'
import type { EndpointData } from "../endpoint-types"

interface PreviewProps {
  data: EndpointData
}

export default function Preview({ data }: PreviewProps) {
  return (
    <div>
      {data.preview}
    </div>
  )
}

