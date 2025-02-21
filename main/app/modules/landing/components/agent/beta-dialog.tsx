'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { WaitlistService } from '@/app/modules/landing/api/api.service';
import { validateEmail } from '@/lib/utils/email-validator';

interface BetaDialogProps {
  trigger: React.ReactNode;
}

export function BetaDialog({ trigger }: BetaDialogProps) {
  const [email, setEmail] = useState('');
  const [socialUrl, setSocialUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [open, setOpen] = useState(false);
  const [showForm, setShowForm] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage(null);

    if (!validateEmail(email)) {
      setMessage({
        type: 'error',
        text: 'Please enter a valid email address'
      });
      setIsLoading(false);
      return;
    }

    const result = await WaitlistService.addToBeta(email, socialUrl);
    
    setMessage({
      type: result.data ? 'success' : 'error',
      text: result.data 
        ? "You've been added to the beta list. We'll be in touch soon!"
        : result.error.message.includes('unique constraint') 
          ? "This email is already on the beta list. We'll be in touch soon!"
          : result.error.message
    });

    if (result.data) {
      setShowForm(false);
      setTimeout(() => {
        setOpen(false);
        setTimeout(() => {
          setEmail('');
          setSocialUrl('');
          setMessage(null);
          setShowForm(true);
        }, 300);
      }, 2000);
    }
    
    setIsLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Join the Beta</DialogTitle>
          <p className="text-sm text-muted-foreground mt-2">
            We'll add you to the app within the next 2 days.
          </p>
        </DialogHeader>
        
        {message && (
          <Alert variant={message.type === 'success' ? 'default' : 'destructive'}>
            <AlertDescription className="text-center">
              {message.text}
            </AlertDescription>
          </Alert>
        )}

        {showForm && (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Email <span className="text-red-500">*</span></Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="socialUrl">Social Profile</Label>
              <Input
                id="socialUrl"
                type="text"
                placeholder="X or LinkedIn url / username"
                value={socialUrl}
                onChange={(e) => setSocialUrl(e.target.value)}
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Joining...' : 'Join Beta'}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}