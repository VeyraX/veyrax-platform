'use client';

import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { Provider } from "../api/types.integrations";
import { disconnectProvider } from "../api/api.integrantions";

interface OAuthButtonProps {
  provider: Provider;
  connected: boolean;
  onConnectionChange?: () => void;
}

export function OAuthButton({ provider, connected, onConnectionChange }: OAuthButtonProps) {
    const [loading, setLoading] = useState(false);

    const handleDisconnect = async () => {
        try {
            setLoading(true);
            await disconnectProvider(provider.id);
            onConnectionChange?.();
        } catch (error) {
            console.error(`Failed to disconnect ${provider.name}:`, error);
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = async () => {
        if (provider.auth_method === 'api_key') {
            console.log('API key flow not implemented');
            return;
        }

        try {
            setLoading(true);
            const response = await fetch(`/api/oauth/${provider.provider_tag}`);
            const { url } = await response.json();
            
            window.location.href = url;
        } catch (error) {
            console.error(`Failed to start OAuth flow for ${provider.name}:`, error);
        } finally {
            setLoading(false);
        }
    };

    if (connected) {
        return (
            <Button 
                variant="ghost" 
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleDisconnect}
                disabled={loading}
            >
                {loading ? (
                    <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    </>
                ) : (
                    'Disconnect'
                )}
            </Button>
        );
    }

    return (
        <Button 
            onClick={handleConnect} 
            disabled={loading}
            variant="outline"
        >
            {loading ? (
                <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                </>
            ) : (
                provider.auth_method === 'api_key' ? 'Enable' : 'Connect'
            )}
        </Button>
    );
}