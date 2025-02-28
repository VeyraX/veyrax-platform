"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProviderDetails, ComponentData } from "../../api/types.integrations"
import { findComponentForEndpoint } from "../../api/api.integrations"
import React from "react"
import DynamicComponentRender from "@/app/modules/agent/components/tools/common/dymanic-component-render"
import { SchemaProperty, ParameterObject } from "../../api/types.integrations"

interface ApiReferenceProps {
  providerDetails: ProviderDetails
}

export default function IntegrationDetailApiReferences({ providerDetails }: ApiReferenceProps) {
  const { provider, endpointsList } = providerDetails
  const [endpointComponents, setEndpointComponents] = useState<Record<string, ComponentData | null>>({})
  const [loading, setLoading] = useState<boolean>(false)

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
    const outputSchema = typeof provider.output_schema === 'string' 
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
      const param: ParameterObject = {
        name,
        type: prop.type || (prop.anyOf ? prop.anyOf.map((t: any) => t.type).filter(Boolean).join(' | ') : 'any'),
        required: required.includes(name),
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
            param.nestedParams.push({
              name: nestedName,
              type: nestedProp.type || (nestedProp.anyOf ? nestedProp.anyOf.map((t: any) => t.type).filter(Boolean).join(' | ') : 'any'),
              required: nestedRequired.includes(nestedName),
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

  const getExampleValue = (prop: SchemaProperty) => {
    if (prop.default !== undefined) return prop.default
    
    if (prop.type === 'string') return "example_string"
    if (prop.type === 'integer' || prop.type === 'number') return 123
    if (prop.type === 'boolean') return true
    if (prop.type === 'array') return []
    if (prop.type === 'object') return {}
    
    if (prop.anyOf) {
      const nonNullType = prop.anyOf.find(t => t.type !== 'null')
      if (nonNullType) {
        if (nonNullType.type === 'string') return "example_string"
        if (nonNullType.type === 'integer' || nonNullType.type === 'number') return 123
        if (nonNullType.type === 'boolean') return true
        if (nonNullType.type === 'array') return []
        if (nonNullType.type === 'object') return {}
      }
    }
    
    return null
  }

  const generateRequestExample = (endpointName: string) => {
    const schema = getEndpointSchema(endpointName)
    if (!schema?.function?.parameters?.properties) return '{}'
    
    const example: Record<string, any> = {}
    const props = schema.function.parameters.properties as Record<string, SchemaProperty>
    
    for (const [name, prop] of Object.entries(props)) {
      if (prop.$ref && schema.function.parameters.$defs) {
        const refName = prop.$ref.split('/').pop() || ''
        const refSchema = schema.function.parameters.$defs[refName]
        
        if (refSchema?.properties) {
          const nestedExample: Record<string, any> = {}
          for (const [nestedName, nestedProp] of Object.entries(refSchema.properties as Record<string, SchemaProperty>)) {
            nestedExample[nestedName] = getExampleValue(nestedProp)
          }
          example[name] = nestedExample
        } else {
          example[name] = {}
        }
      } else {
        example[name] = getExampleValue(prop)
      }
    }
    
    return JSON.stringify(example, null, 2)
  }

  const generateResponseExample = (endpointName: string) => {
    const schema = getOutputSchema(endpointName)
    if (!schema) return '{}'
    
    const example: Record<string, any> = {
      data: {},
      message: "Success"
    }
    
    if (schema.properties?.data?.properties) {
      const dataProps = schema.properties.data.properties as Record<string, SchemaProperty>
      
      if (dataProps.id) {
        example.data = {
          id: "item_123456",
          ...Object.keys(dataProps)
            .filter(key => key !== 'id' && key !== 'component')
            .reduce((obj: Record<string, any>, key) => {
              obj[key] = getExampleValue(dataProps[key])
              return obj
            }, {})
        }
      } 
      else if (dataProps.items) {
        example.data = {
          items: [
            {
              id: "item_123456",
              ...Object.keys((dataProps.items.items?.properties || {}) as Record<string, SchemaProperty>)
                .filter(key => key !== 'id' && key !== 'component')
                .reduce((obj: Record<string, any>, key) => {
                  obj[key] = getExampleValue((dataProps.items.items?.properties || {})[key] as SchemaProperty)
                  return obj
                }, {})
            }
          ],
          next_cursor: "cursor_abc123"
        }
      }
    }
    
    return JSON.stringify(example, null, 2)
  }

  const renderComponentPreview = (endpointName: string) => {
    const component = endpointComponents[endpointName]
    
    if (!component || !component.jsx && !component.component?.jsx) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center text-gray-500 bg-gray-50 rounded-lg border border-gray-200 h-full min-h-[200px]">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"></path>
          </svg>
          <p className="font-medium text-lg text-gray-700">No Component Available</p>
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

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-bold mb-8 border-b pb-2">API Reference</h2>
      
      <div className="space-y-16">
        {endpointsList.map(endpoint => {
          const parameters = getEndpointParameters(endpoint.name);
          const currentEndpoint = endpoint;
          
          return (
            <div key={endpoint.name} id={endpoint.name} className="scroll-mt-20">
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-2xl font-bold">{endpoint.name}</h3>
                  <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100 border-none">
                    {parameters.length} params
                  </Badge>
                </div>
                <p className="text-gray-600">{endpoint.description}</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                <div className="lg:col-span-5">
                  <h4 className="text-lg font-semibold mb-4 text-gray-800">Parameters</h4>

                  <div className="space-y-6">
                    {parameters.map(param => (
                      <div key={param.name} className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                        <div className="flex items-center gap-2 mb-2">
                          <h5 className="font-mono text-sm font-semibold text-gray-900">{param.name}</h5>
                          <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">{param.type}</span>
                          {param.required ? (
                            <Badge className="bg-red-50 text-red-600 hover:bg-red-50 border-none text-xs">
                              required
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-50 text-gray-500 hover:bg-gray-50 border-none text-xs">
                              optional
                            </Badge>
                          )}
                        </div>
                        <p className="text-gray-700 text-sm">{param.description}</p>
                        {param.default && (
                          <p className="text-xs text-gray-500 mt-1">Default: {param.default}</p>
                        )}

                        {param.nestedParams && param.nestedParams.length > 0 && (
                          <div className="mt-4 ml-4 border-l-2 border-gray-100 pl-4">
                            <h6 className="text-xs font-medium text-gray-600 mb-2">
                              {param.name} properties:
                            </h6>
                            <div className="space-y-3">
                              {param.nestedParams.map(nestedParam => (
                                <div key={nestedParam.name} className="bg-gray-50 p-3 rounded-md">
                                  <div className="flex items-center gap-2 mb-1">
                                    <h6 className="font-mono text-xs font-semibold text-gray-800">{nestedParam.name}</h6>
                                    <span className="text-xs px-1.5 py-0.5 bg-gray-100 rounded-full text-gray-600">{nestedParam.type}</span>
                                    {nestedParam.required ? (
                                      <Badge className="bg-red-50 text-red-600 hover:bg-red-50 border-none text-xs">
                                        required
                                      </Badge>
                                    ) : (
                                      <Badge className="bg-gray-50 text-gray-500 hover:bg-gray-50 border-none text-xs">
                                        optional
                                      </Badge>
                                    )}
                                  </div>
                                  <p className="text-xs text-gray-700">{nestedParam.description}</p>
                                  {nestedParam.default && (
                                    <p className="text-xs text-gray-500 mt-1">Default: {nestedParam.default}</p>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}

                    {parameters.length === 0 && (
                      <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
                        <p className="text-gray-500 italic">No parameters required for this endpoint.</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="lg:col-span-7">
                  <Tabs defaultValue="request" className="w-full">
                    <TabsList className="w-full bg-white border border-gray-200 rounded-t-lg p-0 h-12">
                      <TabsTrigger
                        value="request"
                        className="flex-1 rounded-none data-[state=active]:bg-gray-900 data-[state=active]:text-white"
                      >
                        Request
                      </TabsTrigger>
                      <TabsTrigger
                        value="response"
                        className="flex-1 rounded-none data-[state=active]:bg-gray-900 data-[state=active]:text-white"
                      >
                        Response
                      </TabsTrigger>
                      <TabsTrigger
                        value="preview"
                        className="flex-1 rounded-none data-[state=active]:bg-gray-900 data-[state=active]:text-white"
                      >
                        Live Preview
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="request" className="mt-0">
                      <div className="bg-gray-900 text-gray-100 p-4 rounded-b-lg font-mono text-sm overflow-x-auto shadow-md">
                        <pre>{`POST ${currentEndpoint.functionId}

${generateRequestExample(endpoint.name)}`}</pre>
                      </div>
                    </TabsContent>

                    <TabsContent value="response" className="mt-0">
                      <div className="bg-gray-900 text-gray-100 p-4 rounded-b-lg font-mono text-sm overflow-x-auto shadow-md">
                        <pre>{generateResponseExample(endpoint.name)}</pre>
                      </div>
                    </TabsContent>

                    <TabsContent value="preview" className="mt-0">
                      {renderComponentPreview(endpoint.name)}
                    </TabsContent>
                  </Tabs>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}
