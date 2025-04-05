import { NextRequest, NextResponse } from 'next/server';
import { 
    validateUserAuthentication, 
    saveApiKey 
} from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(request: NextRequest) {
    try {
        const requestData = await request.json();
        const { provider_id, api_key, user_id, encrypted_api_key, code } = requestData;
        
        if (!provider_id) {
            return NextResponse.json({ 
                success: false, 
                error: 'Provider ID is required' 
            }, { status: 400 });
        }

        let userId;
        try {
            userId = await validateUserAuthentication({
                user_id,
                encrypted_api_key,
                code
            });
        } catch (authError: any) {
            return NextResponse.json({ 
                success: false, 
                error: authError.message 
            }, { status: 401 });
        }

        // If no API key provided, disconnect the provider
        if (!api_key) {
            const disconnectResponse = await fetch(new URL('/api/integrations/disconnect', request.url).toString(), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ provider_id, user_id: userId })
            });
            
            if (!disconnectResponse.ok) {
                const errorData = await disconnectResponse.json();
                return NextResponse.json({ 
                    success: false, 
                    error: errorData.error || 'Failed to disconnect provider' 
                }, { status: 500 });
            }
            
            return NextResponse.json({ 
                success: true,
                message: 'Provider disconnected successfully'
            });
        }

        try {
            // Save API key using the service function
            const encryptedKey = await saveApiKey({
                user_id: userId,
                provider_id,
                api_key
            });

            return NextResponse.json({ 
                success: true,
                encrypted_api_key: encryptedKey
            });
        } catch (error: any) {
            return NextResponse.json({ 
                success: false, 
                error: error.message 
            }, { status: 500 });
        }

    } catch (error: any) {
        console.error('Error enabling API key provider:', error);
        return NextResponse.json({ 
            success: false, 
            error: error.message || 'Internal server error' 
        }, { status: 500 });
    }
} 