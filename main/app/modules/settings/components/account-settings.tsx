import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { UserProfile } from "../api/types.settings"
import { useEffect, useState } from "react"
import { getUserProfile } from "../api/api.settings"
import { Badge } from "@/components/ui/badge"
import { MoreHorizontal, Plus, LogOut } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { 
  UserSettings, 
  AVAILABLE_LANGUAGES, 
  AVAILABLE_THEMES,
  ThemeOption,
  LanguageOption
} from "../api/types.settings"

export default function AccountSettings() {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [settings, setSettings] = useState<UserSettings>({
    theme: 'system',
    language: 'en'
  })
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    async function loadProfile() {
      const data = await getUserProfile()
      console.log('data', data)
      setProfile(data)
    }
    loadProfile()
  }, [])

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      // TODO: Add your API call here to save settings
      await new Promise(resolve => setTimeout(resolve, 1000)) // Temporary simulation
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Profile Settings</h2>
        <p className="text-sm text-muted-foreground">
          Manage your account settings and set email preferences.
        </p>
      </div>

      <Separator />

      {/* Profile Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Profile</h3>
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            {profile?.avatar_url ? (
              <AvatarImage
                src={profile.avatar_url}
                alt={profile?.full_name ?? 'Profile picture'}
              />
            ) : null}
            <AvatarFallback>
              {profile?.full_name 
                ? profile.full_name.split(' ').map(n => n[0]).join('')
                : 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 space-y-4 my-auto">
            <div className="space-y-2">
              <div>
                <p className="text-foreground font-medium">{profile?.full_name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{profile?.email}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Separator />

      {/* Theme & Language Section */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Preferences</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Theme</label>
            <Select value={settings.theme} onValueChange={(value: ThemeOption) => setSettings(prev => ({ ...prev, theme: value }))}>
              <SelectTrigger>
                <SelectValue placeholder="Select theme" />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_THEMES.map(theme => (
                  <SelectItem key={theme.value} value={theme.value}>
                    {theme.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Language</label>
            <Select value={settings.language} onValueChange={(value: LanguageOption) => setSettings(prev => ({ ...prev, language: value }))}>
              <SelectTrigger>
                <SelectValue placeholder="Select language" />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_LANGUAGES.map(language => (
                  <SelectItem key={language.value} value={language.value}>
                    {language.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Buttons Section */}
      <div className="flex justify-end gap-4">
        <Button 
          onClick={handleSaveSettings} 
          disabled={isSaving}
          variant="outline"
        >
          {isSaving ? "Saving..." : "Save changes"}
        </Button>
      </div>
    </div>
  )
}
