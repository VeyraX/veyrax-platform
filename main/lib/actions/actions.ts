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