"use client"

import { Plus, X } from "lucide-react"
import { useState, useEffect } from "react"
import { convertTableFileToMarkdown } from "@/lib/utils/file-converter"
import { convertTextFileToString } from "@/lib/utils/file-converter"
import { toast } from "sonner"

interface FileUploadProps {
  onFileSelect?: (files: FileList) => void
  onFileRemove?: (fileName: string) => void
  onTableFileSelect?: (markdown: string, fileName: string) => void
  onTextFileSelect?: (text: string, fileName: string) => void
  uploadedFiles?: File[]
  className?: string
  onUploadSuccess?: (data: { sandboxId: string, fileName: string, path: string }) => void
  sandboxId?: string | null
}

export default function FileUpload({ 
  onFileSelect, 
  onFileRemove,
  onTableFileSelect,
  onTextFileSelect,
  uploadedFiles = [],
  className = "",
  onUploadSuccess,
  sandboxId,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [previews, setPreviews] = useState<{[key: string]: string}>({})

  useEffect(() => {
    uploadedFiles.forEach(file => {
      if (!previews[file.name] && file.type.startsWith('image/')) {
        const objectUrl = URL.createObjectURL(file)
        setPreviews(prev => ({
          ...prev,
          [file.name]: objectUrl
        }))
      }
    })

    Object.keys(previews).forEach(fileName => {
      if (!uploadedFiles.find(file => file.name === fileName)) {
        URL.revokeObjectURL(previews[fileName])
        setPreviews(prev => {
          const newPreviews = { ...prev }
          delete newPreviews[fileName]
          return newPreviews
        })
      }
    })
  }, [uploadedFiles])

  

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const removeFile = (fileName: string) => {
    if (previews[fileName]) {
      URL.revokeObjectURL(previews[fileName])
    }
    onFileRemove?.(fileName)
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const fileType = file.name.split('.').pop()?.toLowerCase();
    const allowedImageTypes = ['png', 'jpg', 'jpeg'];
    const allowedTableTypes = ['csv', 'xlsx', 'xls'];
    const allowedTextTypes = ['txt', 'doc', 'docx', 'rtf'];
    
    if (!allowedImageTypes.includes(fileType || '') && 
        !allowedTableTypes.includes(fileType || '') && 
        !allowedTextTypes.includes(fileType || '')) {
      toast.error("File type not supported");
      return;
    }

    try {
      if (allowedTableTypes.includes(fileType || '')) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', `/workspace/${file.name}`);
        if (sandboxId) {
          formData.append('sandboxId', sandboxId);
        }

        const response = await fetch('/api/sandbox/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const result = await response.json();
        onUploadSuccess?.(result);
        
        const markdown = await convertTableFileToMarkdown(file);
        onTableFileSelect?.(markdown, file.name);
      } else if (allowedTextTypes.includes(fileType || '')) {
        const text = await convertTextFileToString(file);
        onTextFileSelect?.(text, file.name);
      }
      
      onFileSelect?.(files);
    } catch (error) {
      console.error('Error processing file:', error);
      toast.error('Failed to upload file');
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative flex flex-col items-center justify-center
        min-h-[64px] w-full rounded-lg
        border-2 border-dashed border-muted
        transition-colors duration-200
        ${uploadedFiles.length === 0 && isDragging ? "border-primary bg-muted/5" : ""}
        ${className}
      `}
    >
      {uploadedFiles.length === 0 && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Plus className="h-4 w-4" />
          Drop files here to add to your message.
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="w-full flex flex-wrap gap-1.5 p-2">
          {uploadedFiles.map((file) => (
            <div 
              key={file.name} 
              className="relative group bg-background border border-border rounded-xl p-1 w-[100px]"
            >
              <button
                onClick={() => removeFile(file.name)}
                className="absolute -right-1 -top-1 z-10 bg-background rounded-full shadow-sm hover:bg-muted p-0.5"
              >
                <X className="h-3 w-3" />
              </button>
              <div className="flex flex-col items-center gap-0.5">
                {previews[file.name] ? (
                  <div className="relative h-10 w-10 bg-muted/30 rounded-lg overflow-hidden">
                    <img 
                      src={previews[file.name]} 
                      alt={file.name} 
                      className="absolute inset-0 h-full w-full object-contain"
                    />
                  </div>
                ) : (
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center text-xs font-medium
                    ${file.name.split('.').pop()?.toLowerCase() === 'xlsx' || 
                      file.name.split('.').pop()?.toLowerCase() === 'xls' || 
                      file.name.split('.').pop()?.toLowerCase() === 'csv' 
                      ? 'bg-green-100 text-green-700'
                      : file.name.split('.').pop()?.toLowerCase() === 'doc' ||
                        file.name.split('.').pop()?.toLowerCase() === 'docx' ||
                        file.name.split('.').pop()?.toLowerCase() === 'rtf'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-muted'}`}>
                    {file.name.split('.').pop()?.toUpperCase()}
                  </div>
                )}
                <span className="text-[10px] text-center w-full truncate px-0.5 text-muted-foreground">
                  {file.name}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
