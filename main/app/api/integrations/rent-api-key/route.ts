import { NextRequest, NextResponse } from 'next/server';
import { validateUserAuthentication, saveRentApiKey } from '@/app/modules/integrations/api/api.integrations.server';
import { canUserRentKeyServer } from '@/app/modules/settings/api/api.server.settings';

export async function POST(request: NextRequest) {
    try {
        const requestData = await request.json();
        const { provider_id, user_id, encrypted_api_key, code } = requestData;
        
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

        const { allowed, reason } = await canUserRentKeyServer(userId);
        if (!allowed) {
            return NextResponse.json({ 
                success: false, 
                error: reason || 'User is not allowed to rent keys' 
            }, { status: 403 });
        }

        try {
            await saveRentApiKey({
                user_id: userId,
                provider_id
            });

            return NextResponse.json({ 
                success: true
            });
        } catch (error: any) {
            return NextResponse.json({ 
                success: false, 
                error: error.message 
            }, { status: 500 });
        }

    } catch (error: any) {
        console.error('Error renting API key:', error);
        return NextResponse.json({ 
            success: false, 
            error: error.message || 'Internal server error' 
        }, { status: 500 });
    }
} 