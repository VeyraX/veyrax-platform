'use client'

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2, AlertCircleIcon, CheckCircle2Icon, Mail } from "lucide-react";
import { toast } from 'sonner';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { submitContactRequest } from '@/app/modules/general/api/general.api'; 
import { Footer } from '../footer';

export default function ContactUsPage() {
  const [email, setEmail] = useState('');
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const resetForm = () => {
    setEmail('');
    setReason('');
    setError(null);
    setSuccess(false);
    setIsSubmitting(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    if (!email || !reason) {
      setError('Please fill in all fields.');
      setIsSubmitting(false);
      return;
    }

    // Basic email validation
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address.');
      setIsSubmitting(false);
      return;
    }

    try {
      await submitContactRequest({ email, reason });
      setSuccess(true);
      toast.success("Message sent!", {
        description: "Thank you for contacting us. We'll get back to you shortly.",
      });
      resetForm();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unexpected error occurred.";
      setError(`Failed to send message: ${errorMessage}`);
      toast.error("Failed to send message.", {
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <main className="flex-grow pb-96">
        <div className="container mx-auto max-w-2xl pt-24 py-8 px-4">
          <div className="flex flex-col items-center mb-6">
            <h1 className="text-4xl md:text-5xl tracking-tighter text-center font-semibold mb-4">
              Have a question?
            </h1>
            <p className="text-base md:text-lg leading-relaxed tracking-tight text-muted-foreground max-w-xl text-center">
              Fill out the form below or send us an email directly. We'll get back to you as soon as possible.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <Alert variant="destructive">
                <AlertCircleIcon className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            {success && (
              <Alert>
                <CheckCircle2Icon className="h-4 w-4 text-green-500" />
                <AlertTitle>Success</AlertTitle>
                <AlertDescription>Your message has been sent successfully!</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email" 
                type="email" 
                placeholder="@example.com" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="reason">Reason / Message</Label>
              <Textarea 
                id="reason"
                placeholder="Tell us how we can help..."
                rows={5}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                disabled={isSubmitting}
                required
              />
            </div>
            
            <div className="flex items-center gap-4 pt-2">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </>
                ) : (
                  "Send Message"
                )}
              </Button>
              
              <Button variant="outline" asChild>
                <a href="mailto:hello@veyrax.com">
                  <Mail className="h-4 w-4" />
                  Send us email instead
                </a>
              </Button>
            </div>
          </form>
        </div>
      </main>
      
      <Footer />
    </div>
  );
}
