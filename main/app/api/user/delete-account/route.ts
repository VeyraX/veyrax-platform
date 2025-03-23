import { createClient } from '@supabase/supabase-js'
import { NextResponse } from 'next/server'
import { createClient as createServerClient } from '@/lib/utils/supabase/server'

export async function POST(request: Request) {
  try {
    const { user_id } = await request.json()
    
    if (!user_id) {
      return NextResponse.json(
        { message: 'Missing user_id parameter' },
        { status: 400 }
      )
    }
    
    const supabase = createServerClient()
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    
    if (userError || !user) {
      console.error('Authentication error:', userError)
      return NextResponse.json(
        { message: 'Authentication required' },
        { status: 401 }
      )
    }
    
    if (user.id !== user_id) {
      return NextResponse.json(
        { message: 'Not authorized to delete this account' },
        { status: 403 }
      )
    }
    
    const adminClient = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!
    )
    
    const { data: tables, error: tablesError } = await adminClient.rpc('get_tables_with_user_id')
      
    if (tablesError) {
      console.error('Error fetching tables with user_id column:', tablesError)
      return NextResponse.json(
        { message: 'Error identifying user data' },
        { status: 500 }
      )
    }
    
    console.log(`Found ${tables?.length || 0} tables with user data for deletion`)
    
    const deletionErrors = []
    
    if (tables && tables.length > 0) {
      for (const { table_name } of tables) {
        console.log(`Deleting user data from ${table_name}`)
        
        try {
          const { error: deleteError } = await adminClient
            .from(table_name)
            .delete()
            .eq('user_id', user_id)
            
          if (deleteError) {
            console.warn(`Error deleting data from ${table_name}:`, deleteError)
            deletionErrors.push({
              table: table_name,
              error: deleteError.message
            })
          }
        } catch (error) {
          console.error(`Exception deleting from ${table_name}:`, error)
          deletionErrors.push({
            table: table_name,
            error: error instanceof Error ? error.message : String(error)
          })
        }
      }
    }
    
    if (deletionErrors.length > 0) {
      console.warn(`Encountered ${deletionErrors.length} errors while deleting user data:`, deletionErrors)
    }
    
    const { error: deleteUserError } = await adminClient.auth.admin.deleteUser(user_id)
    
    if (deleteUserError) {
      console.error('Error deleting user account:', deleteUserError)
      return NextResponse.json(
        { 
          message: 'Failed to delete account',
          details: deleteUserError.message
        },
        { status: 500 }
      )
    }
    
    return NextResponse.json({ 
      success: true,
      message: 'Account successfully deleted',
      dataDeletionErrors: deletionErrors.length > 0 ? deletionErrors : undefined
    })
  } catch (error) {
    console.error('Error in delete account route:', error)
    return NextResponse.json(
      { 
        message: 'Internal server error', 
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    )
  }
}