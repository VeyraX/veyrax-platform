from typing import List, Dict, Any
from db.supabase import get_supabase
import uuid
from datetime import datetime
from typing import Optional
client = get_supabase()

def get_flow_by_id(flow_id: str) -> List[Dict[str, Any]]:
    try:
        flow_data = client.table('user_flows') \
            .select('*') \
            .eq('id', flow_id) \
            .execute()
            
        if not flow_data.data:
            return []
        
        return flow_data.data
    except Exception as e:
        print(f"Error getting flow by id: {e}")
        return []


def get_user_api_key(user_id: str) -> str:
    try:
        api_key_response = client.table('users_api_keys') \
            .select('api_key') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
    
        return api_key_response.data['api_key']
    except Exception as e:
        print(f"Error getting user api key: {e}")
        return None

def create_flow_run(flow_id: str, user_input: Optional[str] = None) -> str:
    try:    
        run_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        client.table('user_flow_runs').insert({
            'run_id': run_id,
            'flow_id': flow_id,
            'user_input': user_input,
            'run_status': 'started',
            'run_at': now,
            'payload': None,
            'completed_at': None
        }).execute()
        
        return run_id
    except Exception as e:
        print(f"Error creating flow run: {e}")
        return None

def update_flow_run_completed(run_id: str, payload: Dict[str, Any], status: str = 'completed') -> None:
    try:
        now = datetime.now().isoformat()
    
        client.table('user_flow_runs').update({
            'run_status': status,
            'completed_at': now,
            'payload': payload
        }).eq('run_id', run_id).execute()
    except Exception as e:
        print(f"Error updating flow run completed: {e}")
