import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { UserProfile } from "../api/types.settings"
import { useEffect, useState } from "react"
import { AlertTriangle } from "lucide-react"
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
import { useTheme } from "next-themes"
import { Skeleton } from "@/components/ui/skeleton"
import { deleteUserAccount } from "../api/api.settings"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { toast } from "sonner"
import { useRouter } from "next/navigation"

interface AccountSettingsProps {
  profile: UserProfile | null;
  isLoading: boolean;
}

export default function AccountSettings({ profile, isLoading }: AccountSettingsProps) {
  const { theme, setTheme } = useTheme()
  const [settings, setSettings] = useState<UserSettings>({
    theme: theme as ThemeOption,
    language: 'en'
  })
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [confirmText, setConfirmText] = useState("")
  const router = useRouter()

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      setTheme(settings.theme)
      await new Promise(resolve => setTimeout(resolve, 1000))
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (confirmText !== "DELETE") return
    
    setIsDeleting(true)
    try {
      const success = await deleteUserAccount()
      if (success) {
        setShowDeleteDialog(false)
        router.push("/")
      } else {
        toast.error("Failed to delete your account. Please try again later.")
      }
    } catch (error) {
      toast.error("Failed to delete your account. Please try again later.")
      console.error("Error deleting account:", error)
    } finally {
      setIsDeleting(false)
      setShowDeleteDialog(false)
    }
  }

  useEffect(() => {
    setSettings(prev => ({ ...prev, theme: theme as ThemeOption }))
  }, [theme])

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
        {isLoading ? (
          <div className="flex items-center gap-4">
            <Skeleton className="h-16 w-16 rounded-full" />
            <div className="flex-1 space-y-4">
              <Skeleton className="h-4 w-[200px]" />
              <Skeleton className="h-3 w-[150px]" />
            </div>
          </div>
        ) : (
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
        )}
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
        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogTrigger asChild>
            <Button variant="destructive">
              Delete Account
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                Delete Account
              </DialogTitle>
              <DialogDescription>
                This action cannot be undone. This will permanently delete your
                account and remove all your data from our servers.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <p className="text-sm font-medium mb-2">
                To confirm, type "DELETE" in the box below:
              </p>
              <Input
                value={confirmText}
                onChange={(e) => setConfirmText(e.target.value)}
                placeholder="DELETE"
                className="mb-4"
              />
            </div>
            <DialogFooter>
              <Button
                variant="ghost"
                onClick={() => {
                  setShowDeleteDialog(false);
                  setConfirmText("");
                }}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteAccount}
                disabled={confirmText !== "DELETE" || isDeleting}
              >
                {isDeleting ? "Deleting..." : "Delete Account"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
