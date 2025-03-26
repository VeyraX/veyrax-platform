'use server'

import { cookies } from "next/headers";
import { createClient } from '@/lib/utils/supabase/server';
import { redirect } from 'next/navigation';
import { headers } from 'next/headers';

export async function GetAuthToken() {
  const cookieStore = cookies();
  return cookieStore.get('authToken')?.value;
}

export async function ValidateCredentials(email: string, password: string): Promise<boolean> {
  const validEmail = process.env.ADMIN_EMAIL || '';
  const validPassword = process.env.ADMIN_PASSWORD || '';
  
  return email === validEmail && password === validPassword;
}

export async function getAccessToken(): Promise<string> {
  try {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No active session');
    }
    
    return session.access_token;
  } catch (error) {
    console.error('getAccessToken error:', error);
    throw new Error('Unauthorized');
  }
}

export async function getAuthHeaders(apiKey?: string): Promise<HeadersInit> {
  try {
    if (apiKey) {
      return {
        'VEYRAX_API_KEY': apiKey,
        'Content-Type': 'application/json'
      };
    }

    const headersList = headers();
    const headerApiKey = headersList.get('VEYRAX_API_KEY');
    if (headerApiKey) {
      return {
        'VEYRAX_API_KEY': headerApiKey,
        'Content-Type': 'application/json'
      };
    }

    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No active session');
    }
    
    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    };
  } catch (error) {
    console.error('Auth error:', error);
    throw error;
  }
}