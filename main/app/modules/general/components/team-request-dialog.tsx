"use client";

import { useState } from "react";
import { toast } from "sonner";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { submitTeamRequest } from "../api/general.api";

interface TeamRequestFormData {
  email: string;
  company: string;
}

interface TeamRequestDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function TeamRequestDialog({ open, onOpenChange }: TeamRequestDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<TeamRequestFormData>({
    email: '',
    company: ''
  });
  const [formErrors, setFormErrors] = useState<{
    email?: string;
    company?: string;
  }>({});

  const validateForm = (): boolean => {
    const errors: {email?: string; company?: string} = {};
    
    if (!formData.email) {
      errors.email = "Email is required";
    } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(formData.email)) {
      errors.email = "Invalid email address";
    }
    
    if (!formData.company) {
      errors.company = "Company name is required";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const onSubmitTeamRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setIsSubmitting(true);
      await submitTeamRequest(formData);
      toast.success("Your request has been submitted. We'll contact you soon!");
      onOpenChange(false);
      setFormData({ email: '', company: '' });
      setFormErrors({});
    } catch (error) {
      console.error("Error submitting team request:", error);
      toast.error("Failed to submit request. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Request Teams Plan</DialogTitle>
          <DialogDescription>
            Fill out this form to get in touch about our custom Teams plan for your business.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmitTeamRequest}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleInputChange}
              />
              {formErrors.email && (
                <p className="text-sm text-red-500">{formErrors.email}</p>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="company">Company Name</Label>
              <Input
                id="company"
                name="company"
                placeholder="Your Company"
                value={formData.company}
                onChange={handleInputChange}
              />
              {formErrors.company && (
                <p className="text-sm text-red-500">{formErrors.company}</p>
              )}
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Submitting..." : "Submit Request"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
} 