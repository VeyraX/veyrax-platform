export interface UserProfile {
    id: string
    email: string | null
    full_name: string | null
    avatar_url: string | null
  }

export type ThemeOption = 'light' | 'dark' | 'system'
export type LanguageOption = 'en' | 'ru' | 'es'

export interface UserSettings {
  theme: ThemeOption
  language: LanguageOption
}

export const DUMMY_SETTINGS: UserSettings = {
  theme: 'system',
  language: 'en'
}

export const AVAILABLE_LANGUAGES: { value: LanguageOption; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'ru', label: 'Русский' },
  { value: 'es', label: 'Español' },
]

export const AVAILABLE_THEMES: { value: ThemeOption; label: string }[] = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
]

export interface UserApiKey {
  id: string;
  created_at: string;
  api_key: string;
  user_id: string;
}

export interface UserSubscription {
  subscription_status: string;
  subscription_start_date: string;
  subscription_end_date: string;
  subscription_id: string;
  cancel_reason: string;
  canceled_at: string;
  is_canceled: boolean;
  amount_usd: number;
  product_name: string;
  price_lookup_key?: string;
  product_id?: string;
  stripe_customer_id?: string;
}

export interface ProductAttributes {
  api_call_count: number | string;
  message_count: number | string;
  active_flow_count: number | string;
  rent_provider_keys: boolean;
  custom_integrations: boolean;
  custom_branding?: boolean;
  account_manager?: boolean;
}

export interface ProductInfo {
  name: string;
  description: string;
  product_tag: 'free' | 'starter' | 'pro' | 'teams';
  stripe_product_id: string;
  attrs: ProductAttributes;
}

export interface UserUsage {
  user_id: string;
  api_call_count: number;
  active_flow_count: number;
  message_count: number;
}