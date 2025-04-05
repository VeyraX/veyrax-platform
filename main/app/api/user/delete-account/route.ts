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
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    )
    
    const { data: tables, error: tablesError } = await adminClient.rpc('get_tables_with_user_id')
      
    if (tablesError) {
      console.error('Error fetching tables with user_id column:', tablesError)
      return NextResponse.json(
        { message: 'Error identifying user data' },
        { status: 500 }
      )
    }
    
    type TableRecord = { table_name: string };
    const deletionErrors: Array<{ table: string, error: string }> = []
    
    if (tables && tables.length > 0) {
      const filteredTables: TableRecord[] = tables.filter(({ table_name }: TableRecord) => {
        if (table_name.endsWith('_view')) return false;
        
        const excludedViews = [
          'user_available_tools',
          'user_provider_scopes_view', 
          'user_actions_flows_view',
          'user_actions_view'
        ];
        
        return !excludedViews.includes(table_name);
      });
      
      console.log('Tables to delete from:', filteredTables.map((t: TableRecord) => t.table_name));
      
      const childTables = ['flow_actions', 'chats_messages'];
      
      for (const childTable of childTables) {
        const tableExists = filteredTables.some((t: TableRecord) => t.table_name === childTable);
        if (tableExists) {
          try {
            console.log(`Deleting from child table: ${childTable}`);
            const { error: deleteError } = await adminClient
              .from(childTable)
              .delete()
              .eq('user_id', user_id);
              
            if (deleteError) {
              console.warn(`Error deleting data from ${childTable}:`, deleteError);
              deletionErrors.push({
                table: childTable,
                error: deleteError.message
              });
            }
          } catch (error) {
            console.error(`Exception deleting from ${childTable}:`, error);
            deletionErrors.push({
              table: childTable,
              error: error instanceof Error ? error.message : String(error)
            });
          }
        }
      }
      
      for (const { table_name } of filteredTables as TableRecord[]) {
        if (childTables.includes(table_name)) continue;
        
        try {
          console.log(`Deleting from table: ${table_name}`);
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