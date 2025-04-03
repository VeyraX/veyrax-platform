"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs-updated"
import { ProviderDetails, ComponentData } from "../../api/types.integrations"
import { findComponentForEndpoint } from "../../api/api.integrations"
import React from "react"
import DynamicComponentRender from "@/app/modules/agent/components/tools/common/dymanic-component-render"
import { SchemaProperty, ParameterObject } from "../../api/types.integrations"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { CheckIcon, CopyIcon } from "lucide-react"
import MobileActionTabs from "./integration-detail-api-reference-mobile-tabs"

interface ApiReferenceProps {
  providerDetails: ProviderDetails
}

export default function IntegrationDetailApiReferences({ providerDetails }: ApiReferenceProps) {
  const { provider, endpointsList } = providerDetails
  const [endpointComponents, setEndpointComponents] = useState<Record<string, ComponentData | null>>({})
  const [loading, setLoading] = useState<boolean>(false)
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const loadComponentsForAllEndpoints = async () => {
      setLoading(true)
      try {
        const components: Record<string, ComponentData | null> = {}
        
        for (const endpoint of endpointsList) {
          const component = await findComponentForEndpoint(provider.provider_tag, endpoint.name)
          components[endpoint.name] = component
        }
        
        setEndpointComponents(components)
      } catch (error) {
        console.error(`Error loading components:`, error)
      } finally {
        setLoading(false)
      }
    }

    loadComponentsForAllEndpoints()
  }, [provider.provider_tag, endpointsList])

  const getEndpointSchema = (endpointName: string) => {
    const inputSchema = typeof provider.input_schema === 'string' 
      ? JSON.parse(provider.input_schema) 
      : provider.input_schema || {}
    
    return inputSchema[endpointName] || null
  }

  const getOutputSchema = (endpointName: string) => {
    const outputSchema = typeof provider.output_schema  === 'string' 
      ? JSON.parse(provider.output_schema) 
      : provider.output_schema || {}
    
    return outputSchema[endpointName] || null
  }

  const getEndpointParameters = (endpointName: string): ParameterObject[] => {
    const schema = getEndpointSchema(endpointName)
    if (!schema?.function?.parameters?.properties) return []
    
    const parameters: ParameterObject[] = []
    
    const props = schema.function.parameters.properties as Record<string, SchemaProperty>
    const required = schema.function.parameters.required || []
    
    for (const [name, prop] of Object.entries(props)) {
      const allowsNull = prop.anyOf && prop.anyOf.some((type: any) => type.type === 'null')
      
      const param: ParameterObject = {
        name,
        type: prop.type || (prop.anyOf ? prop.anyOf.map((t: any) => t.type).filter(Boolean).join(' | ') : 'any'),
        required: !allowsNull && required.includes(name),
        description: prop.description || prop.title || '',
        isRef: !!prop.$ref,
        refName: prop.$ref ? prop.$ref.split('/').pop() || null : null,
        default: prop.default !== undefined ? JSON.stringify(prop.default) : undefined
      }
      parameters.push(param)
    }
    
    if (schema.function.parameters.$defs) {
      for (const param of parameters) {
        if (param.isRef && param.refName && schema.function.parameters.$defs[param.refName]) {
          param.nestedParams = []
          const nestedProps = schema.function.parameters.$defs[param.refName].properties || {}
          const nestedRequired = schema.function.parameters.$defs[param.refName].required || []
          
          for (const [nestedName, nestedProp] of Object.entries(nestedProps as Record<string, SchemaProperty>)) {
            const nestedAllowsNull = nestedProp.anyOf && nestedProp.anyOf.some((type: any) => type.type === 'null')
            
            param.nestedParams.push({
              name: nestedName,
              type: nestedProp.type || (nestedProp.anyOf ? nestedProp.anyOf.map((t: any) => t.type).filter(Boolean).join(' | ') : 'any'),
              required: !nestedAllowsNull && nestedRequired.includes(nestedName),
              description: nestedProp.description || nestedProp.title || '',
              default: nestedProp.default !== undefined ? JSON.stringify(nestedProp.default) : undefined,
              isRef: false,
              refName: null
            })
          }
        }
      }
    }
    
    return parameters
  }

  const generateRequestExample = (endpointName: string) => {
    const exampleSchema = providerDetails.exampleSchema?.[endpointName] || [];
    let requestBody = '{}';
    
    if (exampleSchema.length > 0) {
      const firstExample = exampleSchema[0];
      requestBody = JSON.stringify(firstExample.input, null, 2);
    }
    
    return `curl -X POST 'https://veyraxapp.com/${provider.provider_tag}/${endpointName}' \\
       -H 'VEYRAX_API_KEY: VEYRAX_API_KEY' \\
       -H 'Content-Type: application/json' \\
       -d $'${requestBody}'`;
  }


  const generateResponseExample = (endpointName: string) => {
    const exampleSchema = providerDetails.exampleSchema?.[endpointName] || [];
    if (exampleSchema.length > 0) {
      const firstExample = exampleSchema[0];
      return JSON.stringify(firstExample.output, null, 2);
    }
    
    return JSON.stringify({
      data: {},
      message: "Success"
    }, null, 2);
  }

  const renderComponentPreview = (endpointName: string) => {
    const component = endpointComponents[endpointName]
    
    if (!component || !component.jsx && !component.component?.jsx) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground bg-muted rounded-lg border border-border h-full min-h-[200px]">
          <svg className="w-16 h-16 mx-auto mb-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
          </svg>
          <p className="font-medium text-lg text-foreground">No Component Available</p>
          <p className="text-sm mt-2 max-w-md">This endpoint doesn't have an associated UI component for visualization</p>
        </div>
      )
    }

    const componentData = {
      name: component.name,
      jsx: component.jsx || (component.component?.jsx || ''),
      props: component.exampleProps || {}
    };

    return (
      <div className="p-4 bg-white rounded-lg border border-gray-200">
        <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
          <DynamicComponentRender component={componentData} />
        </div>
      </div>
    )
  }

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedStates(prev => ({ ...prev, [id]: true }));
      
      setTimeout(() => {
        setCopiedStates(prev => ({ ...prev, [id]: false }));
      }, 2000);
    });
  };

  return (
    <div className="mt-12">
      <h2 className="text-3xl font-semibold mb-8 border-b border-border pb-2 text-foreground">Actions details</h2>
      
      <div className="space-y-16">
        {endpointsList.map(endpoint => {
          const parameters = getEndpointParameters(endpoint.name);
          const currentEndpoint = endpoint;
          const requestId = `request-${endpoint.name}`;
          const responseId = `response-${endpoint.name}`;
          const requestText = generateRequestExample(endpoint.name);
          const responseText = generateResponseExample(endpoint.name);
          
          return (
            <div key={endpoint.name} id={endpoint.name} className="scroll-mt-20">
              <MobileActionTabs 
                endpointName={endpoint.name}
                description={endpoint.description}
                parametersCount={parameters.length}
                parameters={parameters}
                requestId={requestId}
                responseId={responseId}
                requestExample={requestText}
                responseExample={responseText}
                copiedStates={copiedStates}
                onCopy={handleCopy}
                renderComponentPreview={() => renderComponentPreview(endpoint.name)}
              />
              
              <div className="hidden md:block">
                <Tabs defaultValue="action" className="w-full">
                  <div className="mb-6 flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-2xl font-bold text-foreground">{endpoint.name}</h3>
                        <Badge className="bg-muted text-muted-foreground hover:bg-muted border-none shadow-none">
                          {parameters.length} params
                        </Badge>
                      </div>
                      <p className="text-muted-foreground">{endpoint.description}</p>
                    </div>
                    
                    <TabsList className="h-auto gap-2 rounded-none bg-transparent px-0 py-1 text-foreground">
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
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                    <div className="lg:col-span-5">
                      <h4 className="text-lg font-semibold mb-4 text-foreground">Body Parameters</h4>

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
                    </div>

                    <div className="lg:col-span-7">
                      <TabsContent value="action" className="mt-0">
                        <div className="space-y-6">
                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <h5 className="text-sm font-medium text-foreground">Request</h5>
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
                                language="json" 
                                style={vscDarkPlus}
                                customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                              >
                                {requestText}
                              </SyntaxHighlighter>
                            </div>
                          </div>

                          <div>
                            <div className="flex justify-between items-center mb-2">
                              <h5 className="text-sm font-medium text-foreground">Response</h5>
                              <button 
                                onClick={() => handleCopy(responseText, responseId)}
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
                                {responseText}
                              </SyntaxHighlighter>
                            </div>
                          </div>
                        </div>
                      </TabsContent>

                      <TabsContent value="component" className="mt-0">
                        {renderComponentPreview(endpoint.name)}
                      </TabsContent>
                    </div>
                  </div>
                </Tabs>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}
