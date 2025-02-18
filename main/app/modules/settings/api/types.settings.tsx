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