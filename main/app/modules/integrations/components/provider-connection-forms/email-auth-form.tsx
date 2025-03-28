import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { CustomAuthField } from "../../api/types.integrations";
import { useState, useEffect } from "react";

interface EmailAuthFormProps {
  authSchema: CustomAuthField[];
  authData: Record<string, any>;
  onChange: (authData: Record<string, any>) => void;
  disabled?: boolean;
}

// Remove all services except Gmail
const EMAIL_SERVICES = [
  { value: "gmail", label: "Gmail" },
];

export function EmailAuthForm({ authSchema, authData, onChange, disabled = false }: EmailAuthFormProps) {
  // No need for selectedService state anymore

  useEffect(() => {
    // Always initialize with gmail
    handleChange("service", "gmail");
  }, []);

  const handleChange = (key: string, value: any) => {
    // Always include service: "gmail" in the data
    onChange({ ...authData, [key]: value, service: "gmail" });
  };

  const renderField = (field: CustomAuthField) => {
    const { key, label, type, required, placeholder, options } = field;
    const value = authData[key] !== undefined ? authData[key] : '';
    
    // Skip service field and only show username and password
    if (key === "service" || !["username", "password"].includes(key)) {
      return null;
    }
    
    // Render only username/password fields
    switch (type) {
      case 'text':
      case 'email':
      case 'url':
      case 'number':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
            </Label>
            <Input
              id={key}
              type={type}
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              required={required}
            />
          </div>
        );
      
      case 'password':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
            </Label>
            <Input
              id={key}
              type="password"
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              placeholder={placeholder || "••••••"}
              disabled={disabled}
              required={required}
            />
          </div>
        );
      
      case 'textarea':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
            </Label>
            <Textarea
              id={key}
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              required={required}
            />
          </div>
        );
      
      case 'select':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
            </Label>
            <Select
              value={value}
              onValueChange={(val) => handleChange(key, val)}
              disabled={disabled}
            >
              <SelectTrigger id={key}>
                <SelectValue placeholder={placeholder || `Select ${label}`} />
              </SelectTrigger>
              <SelectContent>
                {options?.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        );
      
      case 'checkbox':
      case 'boolean':
        return (
          <div className="flex items-center space-x-2" key={key}>
            <Checkbox
              id={key}
              checked={!!value}
              onCheckedChange={(checked) => handleChange(key, checked)}
              disabled={disabled}
            />
            <Label htmlFor={key}>
              {label}
            </Label>
          </div>
        );
      
      default:
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
            </Label>
            <Input
              id={key}
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              required={required}
            />
          </div>
        );
    }
  };

  return (
    <div className="grid grid-cols-1 gap-4">
      {/* Remove service selector UI completely */}
      
      {/* Render username and password fields */}
      {authSchema.map(renderField)}
    </div>
  );
} 