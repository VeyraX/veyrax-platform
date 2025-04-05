import { NextRequest, NextResponse } from 'next/server';
import {
    validateUserAuthentication,
    saveCustomAuth
} from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(request: NextRequest) {
    try {
        const requestData = await request.json();
        const { provider_id, auth_data, user_id, encrypted_api_key, code } = requestData;
        
        if (!provider_id || !auth_data) {
            return NextResponse.json({ 
                success: false, 
                error: 'Provider ID and authentication data are required' 
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

        try {
            await saveCustomAuth({
                user_id: userId,
                provider_id,
                auth_data
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
        console.error('Error updating provider custom auth:', error);
        return NextResponse.json({ 
            success: false, 
            error: error.message || 'Internal server error' 
        }, { status: 500 });
    }
} 