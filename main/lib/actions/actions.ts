'use server'

import { cookies } from "next/headers";

export async function HandleLogin(authToken: string) {
  const cookieStore = cookies();
  cookieStore.set(
    'authToken', 
    authToken,
    {
      maxAge: 60 * 60 * 24 * 30,
    }
  );
}

export async function HandleLogout() {
  const cookieStore = cookies();
  cookieStore.delete('authToken');
}

export async function GetAuthToken() {
  const cookieStore = cookies();
  return cookieStore.get('authToken')?.value;
}

export async function ValidateCredentials(email: string, password: string): Promise<boolean> {
  const validEmail = process.env.ADMIN_EMAIL || '';
  const validPassword = process.env.ADMIN_PASSWORD || '';
  
  return email === validEmail && password === validPassword;
}