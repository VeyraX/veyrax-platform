'use client';

import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { useState, useEffect } from "react"
import { useGetUserApiKey } from "../api/queries.settings"
import { generateApiKey, revokeApiKey } from "../api/api.settings"
import { UserApiKey } from "../api/types.settings"
import { Input } from "@/components/ui/input"
import { Copy, Eye, EyeOff, RefreshCw, AlertTriangle } from "lucide-react"
import { useQueryClient } from "@tanstack/react-query"
import { Alert, AlertDescription } from "@/components/ui/alert"

export default function ApiKeySettings() {
  const queryClient = useQueryClient()
  const { data: apiKey, isLoading } = useGetUserApiKey()
  const [showApiKey, setShowApiKey] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRevoking, setIsRevoking] = useState(false)
  const [copied, setCopied] = useState(false)

  const handleGenerateApiKey = async () => {
    setIsGenerating(true)
    try {
      await generateApiKey()
      queryClient.invalidateQueries({ queryKey: ['user-api-key'] })
    } catch (error) {
      console.error('Error generating API key:', error)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRevokeApiKey = async () => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return
    }
    
    setIsRevoking(true)
    try {
      await revokeApiKey()
      queryClient.invalidateQueries({ queryKey: ['user-api-key'] })
    } catch (error) {
      console.error('Error revoking API key:', error)
    } finally {
      setIsRevoking(false)
    }
  }

  const handleCopyApiKey = () => {
    if (apiKey?.api_key) {
      navigator.clipboard.writeText(apiKey.api_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">API Key</h2>
        <p className="text-sm text-muted-foreground">
          Manage your API key for programmatic access to VeyraX.
        </p>
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Your API Key</h3>
        

        {isLoading ? (
          <div className="h-10 bg-muted animate-pulse rounded-md"></div>
        ) : apiKey ? (
          <div className="space-y-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Input
                  value={apiKey.api_key}
                  readOnly
                  type={showApiKey ? "text" : "password"}
                  className="pr-10 font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              <Button 
                variant="outline" 
                size="icon" 
                onClick={handleCopyApiKey}
                className={copied ? "text-green-600 border-green-600" : ""}
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button 
                variant="outline" 
                size="icon"
                onClick={handleGenerateApiKey}
                disabled={isGenerating}
              >
                <RefreshCw className={`h-4 w-4 ${isGenerating ? "animate-spin" : ""}`} />
              </Button>
            </div>
            
            <div>
              <Button 
                variant="destructive" 
                onClick={handleRevokeApiKey}
                disabled={isRevoking}
              >
                {isRevoking ? "Revoking..." : "Revoke API Key"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <p className="text-muted-foreground">You don't have an API key yet.</p>
            <Button 
              onClick={handleGenerateApiKey}
              disabled={isGenerating}
            >
              {isGenerating ? "Generating..." : "Generate API Key"}
            </Button>
          </div>
        )}
      </div>

      <Separator />

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Usage</h3>
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Use your API key to authenticate requests to the Veyrax API. Include it in the header:
          </p>
          <div className="bg-muted p-3 rounded-md font-mono text-sm overflow-x-auto">
            <pre>VEYRAX_API_KEY: {apiKey?.api_key || 'YOUR_API_KEY'}</pre>
          </div>
        </div>
      </div>
    </div>
  )
}