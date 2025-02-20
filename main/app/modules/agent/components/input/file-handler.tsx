import { useState, useEffect, useRef } from 'react';
import { toast } from "sonner";
import { X } from "lucide-react";

interface FileMetadata {
  sandboxId: string;
  fileName: string;
  path: string;
}

export const useFileHandling = (allowedFileTypes: string[]) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const [previews, setPreviews] = useState<{[key: string]: string}>({});
  const [fileMetadata, setFileMetadata] = useState<FileMetadata | null>(null);
  const [sandboxId, setSandboxId] = useState<string | null>(null);
  const [tableContent, setTableContent] = useState<string | null>(null);
  const [textContent, setTextContent] = useState<string | null>(null);
  const dragCounter = useRef(0);

  useEffect(() => {
    if (!uploadedFiles) return;

    Array.from(uploadedFiles).forEach(file => {
      if (!previews[file.name] && file.type.startsWith('image/')) {
        const objectUrl = URL.createObjectURL(file);
        setPreviews(prev => ({
          ...prev,
          [file.name]: objectUrl
        }));
      }
    });

    return () => {
      Object.values(previews).forEach(url => URL.revokeObjectURL(url));
    };
  }, [uploadedFiles]);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current += 1;
    if (dragCounter.current === 1) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current -= 1;
    if (dragCounter.current === 0) {
      setIsDragging(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current = 0;
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (!files || files.length === 0) return;

    const validFiles = Array.from(files).filter(file => {
      const fileType = file.name.split('.').pop()?.toLowerCase();
      return allowedFileTypes.includes(fileType || '');
    });

    if (validFiles.length === 0) {
      toast.error(`Unsupported file types`, {
        action: {
          label: <X className="h-4 w-4" />,
          onClick: () => console.log("OK clicked")
        }
      });
      return;
    }

    const dataTransfer = new DataTransfer();
    validFiles.forEach(file => dataTransfer.items.add(file));
    handleFileSelect(dataTransfer.files);
  };

  const handleFileSelect = (files: FileList) => {
    setUploadedFiles(files);
  };

  const handleFileRemove = () => {
    if (uploadedFiles) {
      Array.from(uploadedFiles).forEach(file => {
        if (previews[file.name]) {
          URL.revokeObjectURL(previews[file.name]);
        }
      });
    }
    setPreviews({});
    setUploadedFiles(null);
  };

  const handleUploadSuccess = (data: FileMetadata) => {
    setSandboxId(data.sandboxId);
    setFileMetadata(data);
  };

  const handleTableFileSelect = async (markdown: string, fileName: string) => {
    setTableContent(markdown);
  };

  const handleTextFileSelect = async (text: string, fileName: string) => {
    setTextContent(text);
  };

  const resetFileStates = () => {
    handleFileRemove();
    setFileMetadata(null);
    setTableContent(null);
    setTextContent(null);
  };

  return {
    isDragging,
    uploadedFiles,
    previews,
    fileMetadata,
    sandboxId,
    tableContent,
    textContent,
    handlers: {
      handleDragEnter,
      handleDragLeave,
      handleDragOver,
      handleDrop,
      handleFileSelect,
      handleFileRemove,
      handleUploadSuccess,
      handleTableFileSelect,
      handleTextFileSelect,
      resetFileStates
    }
  };
};