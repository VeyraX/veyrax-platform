"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import React from "react"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CheckIcon, CopyIcon } from "lucide-react"
import { McpDetails, Tool, SchemaProperty, ParameterObject } from "@/app/modules/integrations/api/types.integrations.mcp"

interface McpDocumentationProps {
  mcpDetails: McpDetails | null;
  tools: Tool[];
}

export function McpDocumentation({ mcpDetails, tools }: McpDocumentationProps) {
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  const getToolParameters = (tool: Tool): ParameterObject[] => {
    if (!mcpDetails?.input_schema) return [];
    
    // Find the schema for this tool
    const toolSchema = mcpDetails.input_schema.find(schema => schema.name === tool.name);
    if (!toolSchema?.inputSchema) return [];
    
    const schema = typeof toolSchema.inputSchema === 'string' 
      ? JSON.parse(toolSchema.inputSchema) 
      : toolSchema.inputSchema;
    
    if (!schema?.properties) return [];
    
    const parameters: ParameterObject[] = [];
    const props = schema.properties as Record<string, SchemaProperty>;
    const required = schema.required || [];
    
    for (const [name, prop] of Object.entries(props)) {
      const allowsNull = prop.anyOf && prop.anyOf.some((type: any) => type.type === 'null');
      
      const param: ParameterObject = {
        name,
        type: prop.type || (prop.anyOf ? prop.anyOf.map((t: any) => t.type).filter(Boolean).join(' | ') : 'any'),
        required: !allowsNull && required.includes(name),
        description: prop.description || prop.title || '',
        isRef: !!prop.$ref,
        refName: prop.$ref ? prop.$ref.split('/').pop() || null : null,
        default: prop.default !== undefined ? JSON.stringify(prop.default) : undefined
      };
      
      parameters.push(param);
    }
    
    return parameters;
  };

  const generateRequestExample = (tool: Tool) => {
    const parameters = getToolParameters(tool);
    
    // Generate example params object with required params and example values
    const exampleParams: Record<string, any> = {};
    parameters.forEach(param => {
      if (param.required) {
        switch(param.type) {
          case 'string':
            exampleParams[param.name] = `example_${param.name}`;
            break;
          case 'number':
          case 'integer':
            exampleParams[param.name] = 123;
            break;
          case 'boolean':
            exampleParams[param.name] = true;
            break;
          case 'array':
            exampleParams[param.name] = [];
            break;
          case 'object':
            exampleParams[param.name] = {};
            break;
          default:
            exampleParams[param.name] = `example_${param.name}`;
        }
      }
    });
    
    const paramsJson = Object.keys(exampleParams).length > 0 
      ? JSON.stringify(exampleParams, null, 2) 
      : "{}";
    
    return `curl -X POST 'https://veyraxapp.com/tool-call/${mcpDetails?.image_name || "mcp"}/${tool.name}' \\
  -H 'VEYRAX_API_KEY: YOUR_API_KEY' \\
  -H 'Content-Type: application/json' \\
  -d '${paramsJson}'`;
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    });
  };

  return (
    <div className="space-y-8">
      {tools.map(tool => {
        const parameters = getToolParameters(tool);
        const requestId = `request-${tool.id}`;
        const requestText = generateRequestExample(tool);
        
        return (
          <div key={tool.id} id={tool.name} className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 scroll-mt-20">
            <div className="p-6">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-xl font-medium text-foreground">{tool.name}</h3>
                <Badge className="bg-muted text-muted-foreground hover:bg-muted border-none shadow-none">
                  {parameters.length} params
                </Badge>
              </div>
              <p className="text-muted-foreground mb-6">{tool.description}</p>

              <hr className="border-t border-gray-200 dark:border-gray-800 mb-6" />

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Parameters Section */}
                <div>
                  <h4 className="text-lg font-semibold mb-4 text-foreground">Parameters</h4>

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
                        <p>No parameters required for this tool, or schema not available.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Request Example Section */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h5 className="text-sm font-medium text-foreground">Request Example</h5>
                    <button 
                      onClick={() => handleCopy(requestText, requestId)}
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
                      language="bash" 
                      style={vscDarkPlus}
                      customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                    >
                      {requestText}
                    </SyntaxHighlighter>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
      
      {tools.length === 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 text-center text-muted-foreground">
          <p>Tools will show up after deployment.</p>
        </div>
      )}
    </div>
  );
}
