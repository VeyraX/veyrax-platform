import { createClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';
import { 
    validateUserAuthentication, 
    saveDbCredentials,
    disconnectProviderForUser
} from '@/app/modules/integrations/api/api.integrations.server';

export async function POST(request: NextRequest) {
    try {
        const requestData = await request.json();
        const { provider_id, db_config, user_id, encrypted_api_key, code } = requestData;
        
        if (!provider_id || !db_config) {
            return NextResponse.json({ 
                success: false, 
                error: 'Provider ID and database configuration are required' 
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

        const supabase = createClient(
            process.env.SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_KEY!
        );

        const { data: provider } = await supabase
            .from('providers')
            .select('provider_tag')
            .eq('id', provider_id)
            .single();
        
        const isSnowflake = provider?.provider_tag === 'snowflake';
        
        let isValidConfig = true;
        if (isSnowflake) {
            isValidConfig = !!(db_config.account && db_config.user && 
                              db_config.password && db_config.database);
        } else {
            isValidConfig = !!(db_config.host && db_config.port && 
                              db_config.dbname && db_config.user && db_config.password);
        }
        
        if (!isValidConfig) {
            try {
                await disconnectProviderForUser({
                    user_id: userId,
                    provider_id
                });
                
                return NextResponse.json({ 
                    success: true,
                    message: 'Provider disconnected due to missing required fields'
                });
            } catch (error: any) {
                return NextResponse.json({ 
                    success: false, 
                    error: error.message 
                }, { status: 500 });
            }
        }

        try {
            await saveDbCredentials({
                user_id: userId,
                provider_id,
                db_config
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
        console.error('Error enabling DB access provider:', error);
        return NextResponse.json({ 
            success: false, 
            error: error.message || 'Internal server error' 
        }, { status: 500 });
    }
} 