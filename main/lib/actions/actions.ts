'use server'

import { cookies } from "next/headers";
import { createClient } from '@/lib/utils/supabase/server';
import { redirect } from 'next/navigation';

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
    console.log('session', session)
    
    if (!session?.access_token) {
      throw new Error('No active session');
    }
    
    return session.access_token;
  } catch (error) {
    console.error('getAccessToken error:', error);
    throw new Error('Unauthorized');
  }
}

export async function getAuthHeaders(): Promise<HeadersInit> {
  try {
    const supabase = createClient();
    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session?.access_token) {
      throw new Error('No active session');
    }
    
    console.log('Current auth token:', session.access_token.slice(0, 10) + '...');
    return {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json'
    };
  } catch (error) {
    console.error('Auth error:', error);
    throw error;
  }
}