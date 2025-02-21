import { NextRequest, NextResponse } from 'next/server'
import { Sandbox } from '@e2b/code-interpreter'
import { sandboxManager } from '@/lib/utils/sanbox-manager'

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData()
    const file = formData.get('file') as File
    const path = formData.get('path') as string
    const sandboxId = formData.get('sandboxId') as string

    if (!file || !path) {
      return NextResponse.json(
        { message: 'File and path are required' },
        { status: 400 }
      )
    }

    let sandbox: Sandbox
    try {
      if (sandboxId) {
        sandbox = await Sandbox.connect(sandboxId)
      } else {
        const currentSandboxId = sandboxManager.getCurrentSandboxId()
        if (currentSandboxId) {
          sandbox = await Sandbox.connect(currentSandboxId)
        } else {
          sandbox = await sandboxManager.getSandbox()
        }
      }
    } catch (error) {
      console.error('Failed to get sandbox:', error)
      return NextResponse.json(
        { message: 'Failed to initialize sandbox' },
        { status: 500 }
      )
    }

    const arrayBuffer = await file.arrayBuffer()
    await sandbox.files.write(path, new Blob([arrayBuffer]))

    return NextResponse.json({ 
      success: true, 
      sandboxId: sandbox.sandboxId,
      fileName: file.name,
      path: path
    })
  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json(
      { message: error instanceof Error ? error.message : 'Upload failed' },
      { status: 500 }
    )
  }
}