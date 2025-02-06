'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { WaitlistService } from '../api/waitlist.service';
import { validateEmail } from '@/lib/utils/email-validator';

interface WaitlistDialogProps {
  trigger: React.ReactNode;
}

export function WaitlistDialog({ trigger }: WaitlistDialogProps) {
  const [email, setEmail] = useState('');
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

    const result = await WaitlistService.addToWaitlist(email);
    
    setMessage({
      type: result.data ? 'success' : 'error',
      text: result.data 
        ? "You've been added to the waitlist. We'll be in touch soon!"
        : result.error.message.includes('unique constraint') 
          ? "This email is already on the waitlist. We'll be in touch soon!"
          : result.error.message
    });

    if (result.data) {
      setEmail('');
      setShowForm(false);
      setTimeout(() => {
        setOpen(false);
        setMessage(null);
        setShowForm(true);
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
          <DialogTitle>Join the Waitlist</DialogTitle>
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
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Joining...' : 'Join Waitlist'}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}