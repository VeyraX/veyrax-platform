from db.supabase import get_supabase


def split_document(text_content: str, max_length: int = 6000) -> list[tuple[str, int, int]]:
    if len(text_content) <= max_length:
        return [(text_content, 1, 1)]
    
    total_parts = (len(text_content) + max_length - 1) // max_length
    
    parts = []
    for part in range(total_parts):
        start_idx = part * (len(text_content) // total_parts)
        end_idx = (part + 1) * (len(text_content) // total_parts) if part < total_parts - 1 else len(text_content)
        
        if part < total_parts - 1:
            split_point = text_content.find('.', end_idx - 100, end_idx + 100)
            if split_point != -1:
                if part == 0:
                    end_idx = split_point + 1
                else:
                    end_idx = split_point + 1
        
        content_part = text_content[start_idx:end_idx]
        parts.append((content_part, part + 1, total_parts))
    
    return parts


def validate_user_index(user_id: str, collection_name: str) -> bool:
    supabase = get_supabase()
    result = supabase.table('users_provider_indexes') \
        .select('*') \
        .eq('user_id', user_id) \
        .eq('collection_name', collection_name) \
        .execute()
    
    return result.data is not None