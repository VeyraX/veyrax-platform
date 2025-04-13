import { NextRequest, NextResponse } from 'next/server';
import { validateUserAuthentication } from '@/app/modules/integrations/api/api.integrations.server';
import { connectMcpRepository } from '@/app/modules/integrations/api/api.integration.mcp.server';
import { getMcpDetailsByImageName } from '@/app/modules/integrations/api/api.integrations.mcp';

export async function POST(req: NextRequest) {
  try {
    const requestData = await req.json();
    const { image_name, user_id, encrypted_api_key, code, env } = requestData;
    
    if (!image_name) {
      return NextResponse.json({ success: false, error: 'MCP image name is required' }, { status: 400 });
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
    
    const mcpDetails = await getMcpDetailsByImageName(image_name);
    
    if (!mcpDetails) {
      return NextResponse.json({ success: false, error: 'MCP not found' }, { status: 404 });
    }
    
    await connectMcpRepository({
      user_id: userId,
      repo_id: mcpDetails.id,
      env
    });
    
    return NextResponse.json({
      success: true,
      message: 'MCP integration enabled successfully'
    });
    
  } catch (error) {
    console.error('Error enabling MCP:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
} 