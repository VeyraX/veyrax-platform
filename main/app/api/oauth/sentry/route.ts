import { createClient } from '@/lib/utils/supabase/server';
import { createClient as createServiceClient } from '@supabase/supabase-js';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const { scopes, return_url, encrypted_api_key, code } = await request.json();
    
    let supabase;
    let user_id;
    
    if (encrypted_api_key) {
        supabase = createServiceClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL!,
            process.env.SUPABASE_SERVICE_KEY!
        );
    } else {
        supabase = await createClient();
        const { data: { user } } = await supabase.auth.getUser();
        
        if (!user) {
            return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
        }
        user_id = user.id;
    }

    // We don't need to extract useExternalInstall since we're always using external install
    
    const { data: provider } = await supabase
        .from('providers')
        .select('id')
        .eq('provider_tag', 'sentry')
        .single();

    if (!provider) {
        return NextResponse.json({ error: 'Provider not found' }, { status: 404 });
    }

    // Always use the external installation URL for public integrations
    const integrationSlug = process.env.SENTRY_INTEGRATION_SLUG || 'veyrax';
    const externalInstallUrl = `https://sentry.io/sentry-apps/${integrationSlug}/external-install/`;
    
    // Store the provider_id and scopes in state for the callback
    const state = Buffer.from(JSON.stringify({
        provider_id: provider.id,
        scopes,
        return_url: return_url || '/integrations',
        user_id,
        encrypted_api_key,
        code
    })).toString('base64');
    
    // Add state as a query parameter to track the installation
    const urlWithState = `${externalInstallUrl}?state=${state}`;
    
    return NextResponse.json({ url: urlWithState });
}

export { POST as GET }; 