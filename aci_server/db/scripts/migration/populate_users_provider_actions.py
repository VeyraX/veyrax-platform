import sys
import os
import json
from pathlib import Path
import time

# Add the app directory to the Python path
sys.path.append('/app')

from db.supabase import get_supabase
from dotenv import load_dotenv

# Make sure environment variables are loaded
load_dotenv()

def populate_users_provider_actions():
    """
    Заполняет таблицу users_provider_actions на основе:
    1. Для не-OAuth провайдеров: пользователь получает доступ ко всем действиям
    2. Для OAuth провайдеров: проверяем соответствие скоупов токена пользователя и действий
    """
    try:
        # Get Supabase client
        supabase = get_supabase()
        
        # Получаем все провайдеры с их методами аутентификации
        providers_response = supabase.table("providers").select(
            "id, name, auth_method"
        ).execute()
        
        providers = providers_response.data
        print(f"Найдено {len(providers)} провайдеров")
        
        # Разделяем провайдеры на OAuth и не-OAuth
        oauth_providers = [p for p in providers if p["auth_method"] == "oauth"]
        non_oauth_providers = [p for p in providers if p["auth_method"] != "oauth"]
        
        print(f"OAuth провайдеры: {len(oauth_providers)}")
        print(f"Не-OAuth провайдеры: {len(non_oauth_providers)}")
        
        total_links = 0
        
        # Обрабатываем не-OAuth провайдеры (просто связываем всех пользователей со всеми действиями)
        print("\n======= Обработка не-OAuth провайдеров =======")
        for provider in non_oauth_providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            print(f"\nОбработка провайдера: {provider_name}")
            
            # Получаем всех пользователей, подключенных к этому провайдеру
            users_response = supabase.table("users_providers").select(
                "user_id"
            ).eq("provider_id", provider_id).execute()
            
            users = users_response.data
            if not users:
                print(f"Нет пользователей для провайдера {provider_name}. Пропускаем.")
                continue
                
            print(f"Найдено {len(users)} пользователей для провайдера {provider_name}")
            
            # Получаем все действия этого провайдера
            actions_response = supabase.table("provider_actions").select(
                "id, action_name, action_slug"
            ).eq("provider_id", provider_id).execute()
            
            actions = actions_response.data
            if not actions:
                print(f"Нет действий для провайдера {provider_name}. Пропускаем.")
                continue
                
            print(f"Найдено {len(actions)} действий для провайдера {provider_name}")
            
            # Для каждого пользователя добавляем связь со всеми действиями
            user_action_count = 0
            for user in users:
                user_id = user["user_id"]
                for action in actions:
                    action_id = action["id"]
                    
                    # Проверяем, существует ли уже эта связь
                    existing_link = supabase.table("users_provider_actions").select(
                        "id"
                    ).eq("user_id", user_id).eq("action_id", action_id).limit(1).execute()
                    
                    if existing_link.data:
                        # Связь уже существует, пропускаем
                        continue
                    
                    try:
                        # Добавляем связь пользователь-действие
                        supabase.table("users_provider_actions").insert({
                            "user_id": user_id,
                            "action_id": action_id
                        }).execute()
                        
                        user_action_count += 1
                        total_links += 1
                        
                        if user_action_count % 10 == 0:
                            print(f"Создано {user_action_count} связей для провайдера {provider_name}")
                    except Exception as e:
                        if "duplicate key" in str(e).lower():
                            # Еще одна проверка на дублирование (для надежности)
                            pass
                        else:
                            print(f"Ошибка при создании связи для пользователя {user_id} и действия {action_id}: {str(e)}")
            
            print(f"Всего создано {user_action_count} связей для провайдера {provider_name}")
        
        # Обрабатываем OAuth провайдеры (проверяем скоупы)
        print("\n======= Обработка OAuth провайдеров =======")
        for provider in oauth_providers:
            provider_id = provider["id"]
            provider_name = provider["name"]
            
            print(f"\nОбработка OAuth провайдера: {provider_name}")
            
            # Получаем всех пользователей с токенами для этого провайдера
            oauth_users_response = supabase.table("users_oauth_tokens").select(
                "user_id, scopes"
            ).eq("provider_id", provider_id).execute()
            
            oauth_users = oauth_users_response.data
            if not oauth_users:
                print(f"Нет пользователей с OAuth токенами для провайдера {provider_name}. Пропускаем.")
                continue
                
            print(f"Найдено {len(oauth_users)} пользователей с OAuth токенами для провайдера {provider_name}")
            
            # Получаем список пользователей, подключенных к этому провайдеру через users_providers
            connected_users_response = supabase.table("users_providers").select(
                "user_id"
            ).eq("provider_id", provider_id).execute()
            
            connected_user_ids = set(user["user_id"] for user in connected_users_response.data)
            print(f"Найдено {len(connected_user_ids)} пользователей, подключенных к провайдеру {provider_name} в таблице users_providers")
            
            # Получаем все действия этого провайдера
            actions_response = supabase.table("provider_actions").select(
                "id, action_name, action_slug"
            ).eq("provider_id", provider_id).execute()
            
            actions = actions_response.data
            if not actions:
                print(f"Нет действий для провайдера {provider_name}. Пропускаем.")
                continue
                
            print(f"Найдено {len(actions)} действий для провайдера {provider_name}")
            
            # Создаем маппинг действий на требуемые скоупы
            action_required_scopes = {}
            
            for action in actions:
                action_id = action["id"]
                
                # Получаем связи действия со скоупами
                action_scopes_response = supabase.table("provider_action_scopes").select(
                    "scope_id"
                ).eq("action_id", action_id).execute()
                
                action_scope_ids = [item["scope_id"] for item in action_scopes_response.data]
                
                if not action_scope_ids:
                    print(f"Предупреждение: Действие {action['action_name']} не имеет связанных скоупов")
                    continue
                
                # Получаем объекты скоупов
                scopes_response = supabase.table("provider_scopes").select(
                    "scope_id"
                ).in_("id", action_scope_ids).execute()
                
                # Получаем строковые ID скоупов
                required_scope_ids = [scope["scope_id"] for scope in scopes_response.data]
                
                action_required_scopes[action_id] = required_scope_ids
                print(f"Действие {action['action_name']} требует скоупы: {', '.join(required_scope_ids)}")
            
            # Обработка каждого пользователя
            oauth_user_action_count = 0
            skipped_users = 0
            for oauth_user in oauth_users:
                user_id = oauth_user["user_id"]
                
                # Проверяем, что пользователь есть в таблице users_providers
                if user_id not in connected_user_ids:
                    print(f"Пользователь {user_id} имеет OAuth токен, но не найден в таблице users_providers. Пропускаем.")
                    skipped_users += 1
                    continue
                
                user_scopes_str = oauth_user.get("scopes", "")
                
                # Разбор скоупов пользователя
                if not user_scopes_str:
                    print(f"Пользователь {user_id} не имеет скоупов для провайдера {provider_name}")
                    continue
                
                # Преобразуем строку скоупов в список
                user_scopes = []
                if isinstance(user_scopes_str, str):
                    # Разделяем по запятой, если это строка
                    user_scopes = [s.strip() for s in user_scopes_str.split(",")]
                elif isinstance(user_scopes_str, list):
                    # Используем как есть, если это уже список
                    user_scopes = user_scopes_str
                
                print(f"Пользователь {user_id} имеет скоупы: {', '.join(user_scopes)}")
                
                # Проверяем каждое действие
                actions_checked = 0
                actions_added = 0
                actions_skipped = 0
                for action in actions:
                    action_id = action["id"]
                    actions_checked += 1
                    
                    # Пропускаем действия без скоупов
                    if action_id not in action_required_scopes:
                        continue
                    
                    # Проверяем, существует ли уже эта связь
                    existing_link = supabase.table("users_provider_actions").select(
                        "id"
                    ).eq("user_id", user_id).eq("action_id", action_id).limit(1).execute()
                    
                    if existing_link.data:
                        # Связь уже существует, пропускаем
                        actions_skipped += 1
                        continue
                    
                    required_scopes = action_required_scopes[action_id]
                    
                    # Проверяем, есть ли все необходимые скоупы у пользователя
                    has_all_scopes = all(scope in user_scopes for scope in required_scopes)
                    
                    if has_all_scopes:
                        try:
                            # Добавляем связь пользователь-действие
                            supabase.table("users_provider_actions").insert({
                                "user_id": user_id,
                                "action_id": action_id
                            }).execute()
                            
                            actions_added += 1
                            oauth_user_action_count += 1
                            total_links += 1
                            
                        except Exception as e:
                            if "duplicate key" in str(e).lower():
                                # Еще одна проверка на дублирование (для надежности)
                                actions_skipped += 1
                            else:
                                print(f"Ошибка при создании OAuth связи для пользователя {user_id} и действия {action_id}: {str(e)}")
                    else:
                        print(f"Пользователь {user_id} не имеет всех необходимых скоупов для действия {action['action_name']}")
                
                if actions_checked > 0:
                    print(f"Пользователь {user_id}: проверено {actions_checked} действий, добавлено {actions_added}, пропущено {actions_skipped}")
            
            print(f"Всего создано {oauth_user_action_count} OAuth связей для провайдера {provider_name}")
            if skipped_users > 0:
                print(f"Пропущено {skipped_users} пользователей, найденных в OAuth токенах, но не найденных в таблице users_providers")
            
        print(f"\n🎉 Заполнение завершено! Создано {total_links} новых связей пользователь-действие")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении таблицы users_provider_actions: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Вызов основной функции
    populate_users_provider_actions()