import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

const USER_TABLES = [
  'users_providers',
  'user_auth_codes',
  'user_flows',
  'users_api_keys',
  'users_db_access',
  'users_mcp',
  'users_memory',
  'users_oauth_tokens',
  'users_provider_api_keys',
  'users_provider_actions',
  'user_provider_rent_api_keys',
  'users_stripe',
  'user_provider_indexes',
  'integration_requests',
  'chats_chats',
  'api_calls'
];

// Добавляем обработку OPTIONS запроса для CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    }
  });
}

export async function POST(request: Request) {
  try {
    const { old_uid, new_uid } = await request.json();
    
    if (!old_uid || !new_uid) {
      return new NextResponse(
        JSON.stringify({ success: false, error: 'Both old_uid and new_uid are required' }),
        { 
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
          }
        }
      );
    }

    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );

    const { data: oldOmiUser, error: oldOmiError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', old_uid)
      .maybeSingle();
      
    if (oldOmiError) {
      return new NextResponse(
        JSON.stringify({ success: false, error: 'Error fetching old omi_user_id: ' + oldOmiError.message }),
        { 
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
          }
        }
      );
    }
    
    if (!oldOmiUser) {
      return new NextResponse(
        JSON.stringify({ success: false, error: 'Old omi_user_id not found in database' }),
        { 
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
          }
        }
      );
    }
    
    const { data: newOmiUser, error: newOmiError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', new_uid)
      .maybeSingle();
    
    const oldUserId = oldOmiUser.user_id;
    
    const migrationResults = [];
    
    // Сценарий 1: Новый omi_user_id не существует
    if (newOmiError || !newOmiUser) {
      const { error: updateError } = await supabase
        .from('omi_users')
        .update({ omi_user_id: new_uid })
        .eq('omi_user_id', old_uid);
      
      migrationResults.push({
        table: 'omi_users',
        status: updateError ? 'error' : 'updated_omi_id',
        error: updateError ? updateError.message : undefined
      });
      
      return new NextResponse(
        JSON.stringify({
          success: !updateError,
          message: updateError ? 'Failed to update omi_user_id' : 'omi_user_id updated successfully',
          results: migrationResults
        }),
        { 
          status: updateError ? 500 : 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
          }
        }
      );
    }
    
    // Сценарий 2: Полное слияние аккаунтов
    const newUserId = newOmiUser.user_id;
    
    for (const tableName of USER_TABLES) {
      try {
        // Сначала проверим, есть ли записи для старого пользователя
        const { data: countData, error: countError } = await supabase
          .from(tableName)
          .select('*', { count: 'exact', head: true })
          .eq('user_id', oldUserId);
          
        const recordCount = countData ? countData.length : 0;
        
        if (recordCount > 0) {
          const { error } = await supabase
            .from(tableName)
            .update({ user_id: newUserId })
            .eq('user_id', oldUserId);
          
          if (error) {
            migrationResults.push({
              table: tableName,
              status: 'error',
              error: error.message
            });
          } else {
            migrationResults.push({
              table: tableName,
              status: 'success',
              count: recordCount
            });
          }
        } else {
          migrationResults.push({
            table: tableName,
            status: 'skipped',
            count: 0
          });
        }
      } catch (error) {
        migrationResults.push({
          table: tableName,
          status: 'error',
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
    
    const { error: deleteError } = await supabase
      .from('omi_users')
      .delete()
      .eq('omi_user_id', old_uid);
      
    migrationResults.push({
      table: 'omi_users',
      status: deleteError ? 'error' : 'deleted_old_mapping',
      error: deleteError ? deleteError.message : undefined
    });

    return new NextResponse(
      JSON.stringify({
        success: true,
        message: 'Account merge completed',
        results: migrationResults
      }),
      { 
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      }
    );
    
  } catch (error) {
    return new NextResponse(
      JSON.stringify({ 
        success: false, 
        error: 'Failed to merge accounts',
        details: error instanceof Error ? error.message : String(error)
      }),
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      }
    );
  }
} 