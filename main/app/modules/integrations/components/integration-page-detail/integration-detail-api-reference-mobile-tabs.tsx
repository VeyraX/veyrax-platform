import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs-updated";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon } from "lucide-react";
import { ParameterObject } from "../../api/types.integrations";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MobileActionTabsProps {
  endpointName: string;
  description: string;
  parametersCount: number;
  parameters: ParameterObject[];
  requestId: string;
  responseId: string;
  requestExample: string;
  responseExample: string;
  copiedStates: Record<string, boolean>;
  onCopy: (text: string, id: string) => void;
  renderComponentPreview: () => React.ReactNode;
}

export default function MobileActionTabs({
  endpointName,
  description,
  parametersCount,
  parameters,
  requestId,
  responseId,
  requestExample,
  responseExample,
  copiedStates,
  onCopy,
  renderComponentPreview
}: MobileActionTabsProps) {
  return (
    <div className="md:hidden w-full">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <h3 className="text-2xl font-bold text-foreground">{endpointName}</h3>
          <Badge className="bg-muted text-muted-foreground hover:bg-muted border-none shadow-none">
            {parametersCount} params
          </Badge>
        </div>
        <p className="text-muted-foreground">{description}</p>
      </div>

      <Tabs defaultValue="parameters" className="w-full">
        <TabsList className="h-auto gap-2 rounded-none bg-transparent px-0 py-1 text-foreground mb-4">
          <TabsTrigger
            value="parameters"
            className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
          >
            Parameters
          </TabsTrigger>
          <TabsTrigger
            value="action"
            className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
          >
            Action
          </TabsTrigger>
          <TabsTrigger
            value="component"
            className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent"
          >
            Component
          </TabsTrigger>
        </TabsList>

        <TabsContent value="parameters" className="space-y-4 mt-0">
          <div className="space-y-6">
            {parameters.map(param => (
              <div key={param.name}>
                <div className="flex items-center gap-2 mb-2">
                  <h5 className="font-mono text-sm font-semibold text-foreground">{param.name}</h5>
                  <span className="text-xs px-2 py-0.5 bg-muted rounded-md text-muted-foreground">{param.type}</span>
                  {param.required ? (
                    <Badge className="bg-destructive/10 text-destructive hover:bg-destructive/10 border-none text-xs px-2 py-0.5 rounded-md shadow-none">
                      required
                    </Badge>
                  ) : (
                    <Badge className="bg-muted text-muted-foreground hover:bg-muted border-none text-xs px-2 py-0.5 rounded-md shadow-none">
                      optional
                    </Badge>
                  )}
                </div>
                {param.description && 
                 !param.description.match(new RegExp(`^${param.name.replace(/_/g, ' ')}$`, 'i')) && 
                 !param.description.match(new RegExp(`^${param.name}$`, 'i')) &&
                 param.description !== param.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') && (
                  <p className="text-muted-foreground text-sm mb-4">{param.description}</p>
                )}
                {param.default && (
                  <p className="text-xs text-muted-foreground mt-1 mb-4">Default: {param.default}</p>
                )}

                {param.nestedParams && param.nestedParams.length > 0 && (
                  <div className="mt-3 mb-2">
                    <div>
                      {param.nestedParams.map((nestedParam, index) => (
                        <div key={nestedParam.name}>
                          <div className="flex items-center gap-2 mb-1">
                            <h6 className="font-mono text-xs font-semibold text-foreground">{nestedParam.name}</h6>
                            <span className="text-xs px-2 py-0.5 bg-muted rounded-md text-muted-foreground">{nestedParam.type}</span>
                            {nestedParam.required ? (
                              <Badge className="bg-destructive/10 text-destructive hover:bg-destructive/10 border-none text-xs px-2 py-0.5 rounded-md shadow-none">
                                required
                              </Badge>
                            ) : (
                              <Badge className="bg-muted text-muted-foreground hover:bg-muted border-none text-xs px-2 py-0.5 rounded-md shadow-none">
                                optional
                              </Badge>
                            )}
                          </div>
                          {nestedParam.description && 
                           !nestedParam.description.match(new RegExp(`^${nestedParam.name.replace(/_/g, ' ')}$`, 'i')) && 
                           !nestedParam.description.match(new RegExp(`^${nestedParam.name}$`, 'i')) &&
                           nestedParam.description !== nestedParam.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') && (
                            <p className="text-xs text-muted-foreground ml-4">{nestedParam.description}</p>
                          )}
                          {nestedParam.default && (
                            <p className="text-xs text-muted-foreground mt-1 ml-4">Default: {nestedParam.default}</p>
                          )}
                          {index < (param.nestedParams?.length || 0) - 1 && (
                            <hr className="border-t border-border/50 my-2 ml-4" />
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {parameters.indexOf(param) < parameters.length - 1 && (
                  <hr className="border-t border-border my-4" />
                )}
              </div>
            ))}

            {parameters.length === 0 && (
              <div className="text-muted-foreground italic">
                <p>No parameters required for this endpoint.</p>
              </div>
            )}
          </div>
        </TabsContent>

        <TabsContent value="action" className="space-y-4 mt-0">
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-medium text-foreground">Request</h5>
                <button 
                  onClick={() => onCopy(requestExample, requestId)}
                  className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                  aria-label="Copy request"
                >
                  {copiedStates[requestId] ? (
                    <CheckIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="json" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {requestExample}
                </SyntaxHighlighter>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-medium text-foreground">Response</h5>
                <button 
                  onClick={() => onCopy(responseExample, responseId)}
                  className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                  aria-label="Copy response"
                >
                  {copiedStates[responseId] ? (
                    <CheckIcon className="h-4 w-4 text-green-500" />
                  ) : (
                    <CopyIcon className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="json" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {responseExample}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="component" className="space-y-4 mt-0">
          {renderComponentPreview()}
        </TabsContent>
      </Tabs>
    </div>
  );
}