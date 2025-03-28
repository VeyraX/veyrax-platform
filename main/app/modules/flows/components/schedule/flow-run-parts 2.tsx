import { FlowRunPart, ToolInvocation } from "../../api/types.flows";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon } from "lucide-react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from "react";

interface FlowRunPartsProps {
  parts: FlowRunPart[];
}

export function FlowRunParts({ parts }: FlowRunPartsProps) {
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});
  
  const getToolResult = (toolCallId: string) => {
    const toolInvocations = parts[0]?.toolInvocation?.metadata?.toolInvocations;
    if (!toolInvocations) return null;
    
    const toolInvocation = toolInvocations.find(
      (t: ToolInvocation) => t.toolCallId === toolCallId
    );
    return toolInvocation?.result;
  };

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [key]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [key]: false }));
    }, 2000);
  };

  return (
    <div className="space-y-4">
      {parts.map((part, index) => (
        <div 
          key={index} 
          className="rounded-lg border p-4 bg-white w-full"
        >
          {part.type === 'text' ? (
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap text-sm">{part.text}</pre>
            </div>
          ) : (
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="item-1" className="border-none">
                <AccordionTrigger className="hover:no-underline py-1">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="font-medium">{part.toolInvocation?.toolName}</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-4 pt-2">
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <h3 className="text-sm font-medium">Request</h3>
                        <Button 
                          onClick={() => handleCopy(`request-${index}`, JSON.stringify(part.toolInvocation?.args, null, 2))}
                          size="sm"
                          variant="ghost"
                          className="h-6 w-6"
                        >
                          {copiedStates[`request-${index}`] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                        </Button>
                      </div>
                      <SyntaxHighlighter 
                        language="json" 
                        style={vscDarkPlus}
                        customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                      >
                        {JSON.stringify(part.toolInvocation?.args, null, 2)}
                      </SyntaxHighlighter>
                    </div>

                    {getToolResult(part.toolInvocation?.toolCallId!) && (
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <h3 className="text-sm font-medium">Response</h3>
                          <Button 
                            onClick={() => handleCopy(`response-${index}`, JSON.stringify(getToolResult(part.toolInvocation?.toolCallId!), null, 2))}
                            size="sm"
                            variant="ghost"
                            className="h-6 w-6"
                          >
                            {copiedStates[`response-${index}`] ? <CheckIcon className="h-4 w-4" /> : <CopyIcon className="h-4 w-4" />}
                          </Button>
                        </div>
                        <SyntaxHighlighter 
                          language="json" 
                          style={vscDarkPlus}
                          customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                        >
                          {JSON.stringify(getToolResult(part.toolInvocation?.toolCallId!), null, 2)}
                        </SyntaxHighlighter>
                      </div>
                    )}
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          )}
        </div>
      ))}
    </div>
  );
}