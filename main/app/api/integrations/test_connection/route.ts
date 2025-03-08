import { NextRequest, NextResponse } from 'next/server';
import { getAuthHeaders } from '@/lib/actions/actions';

export async function POST(request: NextRequest) {
  try {
    const headers = await getAuthHeaders();
    
    const { providerTag, dbConfig } = await request.json();
    
    if (!providerTag || !dbConfig) {
      return NextResponse.json({ 
        data: {
          success: false,
          message: 'Missing required parameters'
        }
      });
    }
    
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/${providerTag}/test_connection`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(dbConfig),
      credentials: 'include'
    });
    
    const responseData = await response.json();
    console.log(responseData);
    
    return NextResponse.json({
      data: {
        success: responseData.data?.success || false,
        message: responseData.data?.message || 'Connection test completed'
      }
    });
  } catch (error) {
    console.error('Error in test_connection API route:', error);
    return NextResponse.json({ 
      data: {
        success: false,
        message: 'Failed to test connection'
      }
    });
  }
}