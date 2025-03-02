import { createClient } from '@/lib/utils/supabase/server';

const API_BASE_URL = process.env.ACI_SERVER_URL || 'http://localhost:8000';

export async function getUserTools() {
  try {
    const supabase = createClient();
    
    const { data: { session } } = await supabase.auth.getSession();
    const accessToken = session?.access_token;

    if (!accessToken) {
      throw new Error('No access token available');
    }

    const response = await fetch(`${API_BASE_URL}/get-tools`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch user tools: ${response.statusText}`);
    }

    const data = await response.json();
    return data.tools || {};
  } catch (error) {
    console.error('Error in getUserTools:', error);
    return {};
  }
}