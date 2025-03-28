import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
  } from "@/components/ui/accordion";
  import { ScrollArea } from "@/components/ui/scroll-area";
  import { ToolInvocation } from "../../api/types.flows";
  
  interface ToolExecutionDetailsProps {
    executions: ToolInvocation[];
  }
  
  export function ToolExecutionDetails({ executions }: ToolExecutionDetailsProps) {
    return (
      <ScrollArea className="h-[400px] w-full rounded-md border p-4">
        <Accordion type="single" collapsible className="w-full">
          {executions.map((execution, index) => (
            <AccordionItem key={execution.toolCallId} value={`item-${index}`}>
              <AccordionTrigger className="text-sm font-medium">
                <div className="flex items-center gap-2">
                  <span>{execution.toolName}</span>
                  <span className="text-xs text-gray-500">
                    {execution.state || 'completed'}
                  </span>
                </div>
              </AccordionTrigger>
              <AccordionContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold mb-2">Arguments:</h4>
                    <pre className="bg-slate-100 p-2 rounded-md text-xs overflow-x-auto">
                      {JSON.stringify(execution.args, null, 2)}
                    </pre>
                  </div>
                  {execution.result && (
                    <div>
                      <h4 className="text-sm font-semibold mb-2">Result:</h4>
                      <pre className="bg-slate-100 p-2 rounded-md text-xs overflow-x-auto">
                        {JSON.stringify(execution.result, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </ScrollArea>
    );
  }