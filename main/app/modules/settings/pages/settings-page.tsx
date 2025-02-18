import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { X, MoreHorizontal, Bot, UserCircle2, Plus } from "lucide-react"
import Link from "next/link"
import AccountSettings from "../components/account-settings"
import AgentSettings from "../components/agent-settings"
import { useState } from "react"

interface AccountSettingsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AccountSettingsDialog({ open, onOpenChange }: AccountSettingsDialogProps) {
  const [activeTab, setActiveTab] = useState<'account' | 'agent'>('account')

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl p-0 h-[80vh]">
        <div className="flex h-full">
          <div className="w-64 border-r p-6">
            <DialogHeader>
              <DialogTitle className="text-2xl font-semibold tracking-tight">Settings</DialogTitle>
              <p className="text-sm text-muted-foreground">Manage your account info.</p>
            </DialogHeader>

            <nav className="space-y-0.5 -ml-3 mt-4">
              <Link
                href="#"
                onClick={() => setActiveTab('account')}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'account' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <UserCircle2 className="h-3.5 w-3.5" />
                <span>Account</span>
              </Link>
              <Link
                href="#"
                onClick={() => setActiveTab('agent')}
                className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-sm ${
                  activeTab === 'agent' 
                    ? 'bg-secondary text-secondary-foreground' 
                    : 'text-muted-foreground hover:bg-secondary'
                }`}
              >
                <Bot className="h-3.5 w-3.5" />
                <span>Agent</span>
              </Link>
            </nav>
          </div>

          <div className="flex-1 p-6 overflow-y-auto">
            {activeTab === 'account' ? <AccountSettings /> : <AgentSettings />}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}