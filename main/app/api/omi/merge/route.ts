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

export async function POST(request: Request) {
  try {
    console.log('🔄 Starting account merge process');
    const { old_uid, new_uid } = await request.json();
    console.log(`📝 Received request to merge: old_omi_id=${old_uid}, new_omi_id=${new_uid}`);
    
    if (!old_uid || !new_uid) {
      console.log('❌ Missing required parameters');
      return NextResponse.json(
        { success: false, error: 'Both old_uid and new_uid are required' },
        { status: 400 }
      );
    }

    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    );
    console.log('✅ Supabase client initialized');

    console.log(`🔍 Looking up user_id for old_omi_id=${old_uid}`);
    const { data: oldOmiUser, error: oldOmiError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', old_uid)
      .maybeSingle();
      
    if (oldOmiError) {
      console.error('❌ Error fetching old omi_user_id:', oldOmiError);
      return NextResponse.json(
        { success: false, error: 'Error fetching old omi_user_id: ' + oldOmiError.message },
        { status: 500 }
      );
    }
    
    if (!oldOmiUser) {
      console.log(`❌ Old omi_user_id=${old_uid} not found in database`);
      return NextResponse.json(
        { success: false, error: 'Old omi_user_id not found in database' },
        { status: 400 }
      );
    }
    
    console.log(`✅ Found user_id=${oldOmiUser.user_id} for old_omi_id=${old_uid}`);
    
    console.log(`🔍 Looking up user_id for new_omi_id=${new_uid}`);
    const { data: newOmiUser, error: newOmiError } = await supabase
      .from('omi_users')
      .select('user_id')
      .eq('omi_user_id', new_uid)
      .maybeSingle();
    
    const oldUserId = oldOmiUser.user_id;
    console.log(`📋 Old user_id: ${oldUserId}`);
    
    const migrationResults = [];
    
    // Сценарий 1: Новый omi_user_id не существует
    if (newOmiError || !newOmiUser) {
      console.log(`ℹ️ New omi_user_id=${new_uid} not found. Simple update scenario.`);
      console.log(`🔄 Updating omi_user_id from ${old_uid} to ${new_uid}`);
      
      const { error: updateError } = await supabase
        .from('omi_users')
        .update({ omi_user_id: new_uid })
        .eq('omi_user_id', old_uid);
      
      if (updateError) {
        console.error('❌ Error updating omi_user_id:', updateError);
      } else {
        console.log('✅ Successfully updated omi_user_id');
      }
        
      migrationResults.push({
        table: 'omi_users',
        status: updateError ? 'error' : 'updated_omi_id',
        error: updateError ? updateError.message : undefined
      });
      
      return NextResponse.json({
        success: !updateError,
        message: updateError ? 'Failed to update omi_user_id' : 'omi_user_id updated successfully',
        results: migrationResults
      });
    }
    
    // Сценарий 2: Полное слияние аккаунтов
    const newUserId = newOmiUser.user_id;
    console.log(`📋 New user_id: ${newUserId}`);
    console.log(`🔄 Full merge scenario: Merging user data from ${oldUserId} to ${newUserId}`);
    
    console.log(`📊 Starting migration of ${USER_TABLES.length} tables`);
    for (const tableName of USER_TABLES) {
      try {
        console.log(`⏳ Processing table: ${tableName}`);
        
        // Сначала проверим, есть ли записи для старого пользователя
        const { data: countData, error: countError } = await supabase
          .from(tableName)
          .select('*', { count: 'exact', head: true })
          .eq('user_id', oldUserId);
          
        const recordCount = countData ? countData.length : 0;
        console.log(`📊 Found ${recordCount} records in ${tableName} for old user_id`);
        
        if (recordCount > 0) {
          console.log(`🔄 Updating user_id from ${oldUserId} to ${newUserId} in ${tableName}`);
          const { error } = await supabase
            .from(tableName)
            .update({ user_id: newUserId })
            .eq('user_id', oldUserId);
          
          if (error) {
            console.error(`❌ Error updating ${tableName}:`, error);
            migrationResults.push({
              table: tableName,
              status: 'error',
              error: error.message
            });
          } else {
            console.log(`✅ Successfully updated ${recordCount} records in ${tableName}`);
            migrationResults.push({
              table: tableName,
              status: 'success',
              count: recordCount
            });
          }
        } else {
          console.log(`ℹ️ No records to update in ${tableName}`);
          migrationResults.push({
            table: tableName,
            status: 'skipped',
            count: 0
          });
        }
      } catch (error) {
        console.error(`❌ Error processing table ${tableName}:`, error);
        migrationResults.push({
          table: tableName,
          status: 'error',
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }
    
    console.log(`🗑️ Deleting old omi_user mapping for omi_user_id=${old_uid}`);
    const { error: deleteError } = await supabase
      .from('omi_users')
      .delete()
      .eq('omi_user_id', old_uid);
      
    if (deleteError) {
      console.error('❌ Error deleting old omi_user mapping:', deleteError);
    } else {
      console.log('✅ Successfully deleted old omi_user mapping');
    }
      
    migrationResults.push({
      table: 'omi_users',
      status: deleteError ? 'error' : 'deleted_old_mapping',
      error: deleteError ? deleteError.message : undefined
    });

    console.log('✅ Account merge completed successfully');
    return NextResponse.json({
      success: true,
      message: 'Account merge completed',
      results: migrationResults
    });
    
  } catch (error) {
    console.error('❌ Unexpected error during account merge:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to merge accounts',
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}
