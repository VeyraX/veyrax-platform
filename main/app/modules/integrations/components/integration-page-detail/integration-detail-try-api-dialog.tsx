"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { ParameterObject } from "../../api/types.integrations"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Loader2, PlayIcon } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface TryApiDialogProps {
  providerTag: string
  endpointName: string
  parameters: ParameterObject[]
  apiKey?: string
}

export default function IntegrationTryApiDialog({ 
  providerTag, 
  endpointName, 
  parameters,
  apiKey
}: TryApiDialogProps) {
  const [formValues, setFormValues] = useState<Record<string, any>>({})
  const [nestedValues, setNestedValues] = useState<Record<string, Record<string, any>>>({})
  const [response, setResponse] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [userApiKey, setUserApiKey] = useState(apiKey || "")
  const [open, setOpen] = useState(false)

  const handleInputChange = (paramName: string, value: any) => {
    setFormValues(prev => ({
      ...prev,
      [paramName]: value
    }))
  }

  const handleNestedInputChange = (parentParam: string, paramName: string, value: any) => {
    setNestedValues(prev => ({
      ...prev,
      [parentParam]: {
        ...(prev[parentParam] || {}),
        [paramName]: value
      }
    }))
  }

  const prepareRequestBody = () => {
    const requestBody: Record<string, any> = { ...formValues }
    
    // Add nested parameters
    Object.entries(nestedValues).forEach(([parentKey, nestedObj]) => {
      if (Object.keys(nestedObj).length > 0) {
        requestBody[parentKey] = nestedObj
      }
    })
    
    return requestBody
  }

  const handleSubmit = async () => {
    if (!userApiKey) {
      setError("API Key is required")
      return
    }

    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const requestBody = prepareRequestBody()
      
      const response = await fetch(`https://api.veyrax.com/${providerTag}/${endpointName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': userApiKey
        },
        body: JSON.stringify(requestBody)
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to fetch data')
      }
      
      setResponse(JSON.stringify(data, null, 2))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setLoading(false)
    }
  }

  const renderParameterInput = (param: ParameterObject) => {
    if (param.isRef && param.nestedParams && param.nestedParams.length > 0) {
      return (
        <div key={param.name} className="space-y-4 mb-6">
          <div className="flex flex-col space-y-1.5">
            <Label htmlFor={param.name} className="flex items-center gap-2">
              {param.name}
              {param.required && <span className="text-destructive text-xs">*</span>}
            </Label>
            {param.description && (
              <p className="text-xs text-muted-foreground">{param.description}</p>
            )}
          </div>
          
          <div className="border border-border rounded-md p-4 space-y-4">
            <p className="text-sm font-medium">{param.refName} Properties</p>
            {param.nestedParams.map(nestedParam => (
              <div key={`${param.name}-${nestedParam.name}`} className="space-y-1.5">
                <Label htmlFor={`${param.name}-${nestedParam.name}`} className="flex items-center gap-2">
                  {nestedParam.name}
                  {nestedParam.required && <span className="text-destructive text-xs">*</span>}
                </Label>
                {nestedParam.description && (
                  <p className="text-xs text-muted-foreground">{nestedParam.description}</p>
                )}
                {nestedParam.type === 'boolean' ? (
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id={`${param.name}-${nestedParam.name}`}
                      checked={nestedValues[param.name]?.[nestedParam.name] || false}
                      onCheckedChange={(checked) => 
                        handleNestedInputChange(param.name, nestedParam.name, checked)
                      }
                    />
                    <label 
                      htmlFor={`${param.name}-${nestedParam.name}`}
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      {nestedParam.name}
                    </label>
                  </div>
                ) : nestedParam.type === 'string' && nestedParam.description?.includes('multiline') ? (
                  <Textarea
                    id={`${param.name}-${nestedParam.name}`}
                    value={nestedValues[param.name]?.[nestedParam.name] || ''}
                    onChange={(e) => handleNestedInputChange(param.name, nestedParam.name, e.target.value)}
                    placeholder={`Enter ${nestedParam.name}...`}
                    className="resize-y"
                  />
                ) : (
                  <Input
                    id={`${param.name}-${nestedParam.name}`}
                    type={nestedParam.type === 'number' ? 'number' : 'text'}
                    value={nestedValues[param.name]?.[nestedParam.name] || ''}
                    onChange={(e) => {
                      const value = nestedParam.type === 'number' 
                        ? parseFloat(e.target.value) 
                        : e.target.value
                      handleNestedInputChange(param.name, nestedParam.name, value)
                    }}
                    placeholder={`Enter ${nestedParam.name}...`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )
    }

    return (
      <div key={param.name} className="space-y-1.5 mb-6">
        <Label htmlFor={param.name} className="flex items-center gap-2">
          {param.name}
          {param.required && <span className="text-destructive text-xs">*</span>}
        </Label>
        {param.description && (
          <p className="text-xs text-muted-foreground">{param.description}</p>
        )}
        {param.type === 'boolean' ? (
          <div className="flex items-center space-x-2">
            <Checkbox 
              id={param.name}
              checked={formValues[param.name] || false}
              onCheckedChange={(checked) => handleInputChange(param.name, checked)}
            />
            <label 
              htmlFor={param.name}
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
            >
              {param.name}
            </label>
          </div>
        ) : param.type === 'string' && param.description?.includes('multiline') ? (
          <Textarea
            id={param.name}
            value={formValues[param.name] || ''}
            onChange={(e) => handleInputChange(param.name, e.target.value)}
            placeholder={`Enter ${param.name}...`}
            className="resize-y"
          />
        ) : (
          <Input
            id={param.name}
            type={param.type === 'number' ? 'number' : 'text'}
            value={formValues[param.name] || ''}
            onChange={(e) => {
              const value = param.type === 'number' 
                ? parseFloat(e.target.value) 
                : e.target.value
              handleInputChange(param.name, value)
            }}
            placeholder={`Enter ${param.name}...`}
          />
        )}
      </div>
    )
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <PlayIcon className="h-4 w-4" />
          Try this
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Try {endpointName} API</DialogTitle>
        </DialogHeader>
        
        <div className="grid gap-6 py-4">
          <div className="space-y-1.5">
            <Label htmlFor="api-key" className="flex items-center gap-2">
              API Key <span className="text-destructive text-xs">*</span>
            </Label>
            <Input
              id="api-key"
              value={userApiKey}
              onChange={(e) => setUserApiKey(e.target.value)}
              placeholder="Enter your Veyrax API key"
              type="password"
            />
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-medium">Parameters</h3>
            
            {parameters.length === 0 ? (
              <p className="text-sm text-muted-foreground">This endpoint doesn't require any parameters.</p>
            ) : (
              parameters.map(renderParameterInput)
            )}
          </div>

          <Button 
            onClick={handleSubmit} 
            disabled={loading}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Sending request...
              </>
            ) : (
              'Send Request'
            )}
          </Button>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {response && (
            <div className="space-y-2">
              <h3 className="text-lg font-medium">Response</h3>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="json" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {response}
                </SyntaxHighlighter>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}