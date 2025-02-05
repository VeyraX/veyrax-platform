import type { EndpointData } from "../../endpoint-types"
import { useState } from "react"
import { FileTree } from "./endpoint-code-file-tree"
import { CodeDisplay } from "./endpoint-code"

interface CodeProps {
  data: EndpointData
}

export default function EndpointCodeMain({ data }: CodeProps) {
  const [selectedFileId, setSelectedFileId] = useState<string | null>(() => {
    return data.code && data.code.length > 0 ? 'file-0' : null
  })
  
  const handleFileSelect = (id: string) => {
    const fileIndex = parseInt(id.split('-')[1])
    setSelectedFileId(`file-${fileIndex}`)
  }

  const selectedFile = selectedFileId 
    ? data.code.find((_, index) => `file-${index}` === selectedFileId)
    : null

  return (
    <div className="flex gap-4">
      {data.code && data.code.length > 0 && (
        <FileTree 
          code={data.code}
          onFileSelect={handleFileSelect}
        />
      )}
      <CodeDisplay selectedFile={selectedFile || null} />
    </div>
  )
}