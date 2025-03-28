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

const EMAIL_SERVICES = [
  { value: "gmail", label: "Gmail" },
  { value: "outlook", label: "Outlook / Office 365" },
  { value: "yahoo", label: "Yahoo Mail" },
  { value: "zoho", label: "Zoho Mail" },
  { value: "aol", label: "AOL Mail" },
  { value: "protonmail", label: "ProtonMail" },
  { value: "gmx", label: "GMX Mail" },
  { value: "other", label: "Other Email Provider" }
];

export function EmailAuthForm({ authSchema, authData, onChange, disabled = false }: EmailAuthFormProps) {
  const [selectedService, setSelectedService] = useState<string>(authData.service || "gmail");

  useEffect(() => {
    // Initialize with gmail if not set
    if (!authData.service) {
      handleChange("service", "gmail");
    } else {
      setSelectedService(authData.service);
    }
  }, []);

  const handleChange = (key: string, value: any) => {
    onChange({ ...authData, [key]: value });
  };

  const handleServiceChange = (service: string) => {
    setSelectedService(service);
    handleChange("service", service);
    
    // Clear any custom server settings when switching to a standard service
    if (service !== "other") {
      const newAuthData = { ...authData, service };
      // Keep only username and password when switching to a standard service
      onChange({
        username: authData.username || "",
        password: authData.password || "",
        service
      });
    }
  };

  const renderField = (field: CustomAuthField) => {
    const { key, label, type, required, placeholder, options } = field;
    const value = authData[key] !== undefined ? authData[key] : '';
    
    // Skip rendering service field as we handle it separately
    if (key === "service") return null;
    
    // For standard services, only show username and password
    if (selectedService !== "other" && !["username", "password"].includes(key)) {
      return null;
    }
    
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
      {/* Service Selector - always visible */}
      <div className="space-y-2">
        <Label htmlFor="service">Email Service</Label>
        <Select
          value={selectedService}
          onValueChange={handleServiceChange}
          disabled={disabled}
        >
          <SelectTrigger id="service">
            <SelectValue placeholder="Select Email Service" />
          </SelectTrigger>
          <SelectContent>
            {EMAIL_SERVICES.map((service) => (
              <SelectItem key={service.value} value={service.value}>
                {service.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      
      {/* If service is other, show a note about required fields */}
      {selectedService === "other" && (
        <div className="text-sm text-muted-foreground">
          All fields below are required for custom email providers.
        </div>
      )}
      
      {/* Render other auth fields */}
      {authSchema.map(renderField)}
    </div>
  );
} 