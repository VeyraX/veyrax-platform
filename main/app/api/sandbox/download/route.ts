import { NextRequest, NextResponse } from 'next/server';
import { Sandbox } from '@e2b/code-interpreter';
import { sandboxManager } from '@/lib/utils/sanbox-manager';

export async function GET(request: NextRequest) {
  const path = request.nextUrl.searchParams.get('path');
  const sandboxId = request.nextUrl.searchParams.get('sandboxId');
  
  if (!path || !sandboxId) {
    return NextResponse.json({ error: 'Path and sandboxId are required' }, { status: 400 });
  }

  try {
    let sandboxToUse = sandboxId || sandboxManager.getCurrentSandboxId();
    
    if (!sandboxToUse) {
      return NextResponse.json({ error: 'No active sandbox found' }, { status: 400 });
    }

    const sandbox = await Sandbox.connect(sandboxToUse);
    const fileContent = await sandbox.files.read(path);
    const fileName = path.split('/').pop();
    
    const fileExtension = fileName?.split('.').pop()?.toLowerCase();
    let contentType = 'application/octet-stream';
    
    if (fileExtension) {
      switch (fileExtension) {
        case 'xlsx':
          contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          break;
        case 'xls':
          contentType = 'application/vnd.ms-excel';
          break;
        case 'csv':
          contentType = 'text/csv';
          break;
      }
    }

    const buffer = Buffer.from(fileContent);
    
    return new NextResponse(buffer, {
      headers: {
        'Content-Disposition': `attachment; filename="${fileName}"`,
        'Content-Type': contentType,
        'Content-Length': buffer.length.toString(),
      },
    });
  } catch (error) {
    console.error('Download error:', error);
    return NextResponse.json({ error: 'Failed to download file' }, { status: 500 });
  }
}