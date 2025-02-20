import React from "react"
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Button } from "@/components/ui/button"
import { Check, Copy } from "lucide-react"

export function MessageFormatter({ content }: { content: string }) {
  return (
    <ReactMarkdown
      components={{
        code({ node, inline, className, children, ...props }: {
          node?: any;
          inline?: boolean;
          className?: string;
          children?: React.ReactNode;
        } & React.HTMLAttributes<HTMLElement>) {
          const match = /language-(\w+)/.exec(className || '')
          const [isCopied, setIsCopied] = React.useState(false)

          React.useEffect(() => {
            if (isCopied) {
              const timer = setTimeout(() => setIsCopied(false), 2000)
              return () => clearTimeout(timer)
            }
          }, [isCopied])

          return !inline && match ? (
            <div className="relative rounded-lg overflow-hidden max-w-full">
              <Button
                variant="ghost"
                size="icon"
                className="absolute right-2 top-2 h-8 w-8 text-white hover:text-white hover:bg-white/10"
                onClick={() => {
                  navigator.clipboard.writeText(String(children))
                  setIsCopied(true)
                }}
              >
                {isCopied ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
              <SyntaxHighlighter
                {...props}
                style={vscDarkPlus}
                language={match[1]}
                PreTag="div"
                className="rounded-lg"
                customStyle={{ 
                  overflow: 'auto',
                  maxWidth: 'min(900px, 100%)',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  backgroundColor: '#1e1e1e',
                }}
              >
                {String(children).replace(/\n$/, '')}
              </SyntaxHighlighter>
            </div>
          ) : (
            <code {...props} className={className}>
              {children}
            </code>
          )
        },
        p({ node, children }) {
          return <p className="my-2 whitespace-pre-wrap">{children}</p>
        },
        ul: ({node, ...props}) => <ul className="pl-4 my-2 list-disc" {...props}/>,
        ol: ({node, ...props}) => <ol className="pl-4 my-2 list-decimal" {...props}/>,
        li: ({node, ...props}) => <li className="my-1" {...props}/>,
        h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-4" {...props}/>,
        h2: ({node, ...props}) => <h2 className="text-xl font-semibold my-3" {...props}/>,
        h3: ({node, ...props}) => <h3 className="text-lg font-medium my-2" {...props}/>,
        a: ({node, ...props}) => (
          <a 
            className="text-blue-500 hover:text-blue-600 hover:underline" 
            target="_blank" 
            rel="noopener noreferrer" 
            {...props}
          />
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  )
}