import { EditorView, basicSetup } from 'codemirror'
import { javascript } from '@codemirror/lang-javascript'
import { python } from '@codemirror/lang-python'
import { java } from '@codemirror/lang-java'
import { useEffect, useRef } from 'react'

interface CodeDisplayProps {
  selectedFile: { path: string; snippet: string } | null
}

export function CodeDisplay({ selectedFile }: CodeDisplayProps) {
  const editorRef = useRef<HTMLDivElement>(null)
  const viewRef = useRef<EditorView | null>(null)

  const getLanguage = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'ts':
      case 'tsx':
      case 'js':
      case 'jsx':
        return javascript()
      case 'py':
        return python()
      case 'java':
        return java()
      default:
        return javascript()
    }
  }

  useEffect(() => {
    if (!selectedFile || !editorRef.current) return

    if (viewRef.current) {
      viewRef.current.destroy()
    }

    const view = new EditorView({
      doc: selectedFile.snippet,
      extensions: [
        basicSetup,
        getLanguage(selectedFile.path),
        EditorView.editable.of(false),
        EditorView.theme({
          '&': { height: '100%' },
          '.cm-scroller': { overflow: 'auto' },
        }),
      ],
      parent: editorRef.current,
    })

    viewRef.current = view

    return () => {
      view.destroy()
    }
  }, [selectedFile])

  return (
    <div className="flex-1 overflow-hidden">
      {selectedFile ? (
        <div ref={editorRef} className="h-full rounded-lg overflow-hidden" />
      ) : (
        <div className="text-gray-500">Select a file to view its code</div>
      )}
    </div>
  )
}