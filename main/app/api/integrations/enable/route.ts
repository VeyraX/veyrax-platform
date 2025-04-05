import { NextRequest, NextResponse } from 'next/server';
import { 
    validateUserAuthentication, 
    saveEnableProvider
} from '@/app/modules/integrations/api/api.integrations.server';

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

        try {
            await saveEnableProvider({
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
        console.error('Error enabling provider:', error);
        return NextResponse.json({ 
            success: false, 
            error: error.message || 'Internal server error' 
        }, { status: 500 });
    }
} 