import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { CustomAuthField } from "../../api/types.integrations";
import { useState, useEffect } from "react";

interface CustomAuthFormProps {
  authSchema: CustomAuthField[];
  authData: Record<string, any>;
  onChange: (authData: Record<string, any>) => void;
  disabled?: boolean;
}

export function CustomAuthForm({ authSchema, authData, onChange, disabled = false }: CustomAuthFormProps) {
  const handleChange = (key: string, value: any) => {
    onChange({ ...authData, [key]: value });
  };

  const renderField = (field: CustomAuthField) => {
    const { key, label, type, required, placeholder, options } = field;
    const value = authData[key] !== undefined ? authData[key] : '';
    
    switch (type) {
      case 'text':
      case 'email':
      case 'url':
      case 'number':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
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
              {required && <span className="text-red-500 ml-1">*</span>}
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
              {required && <span className="text-red-500 ml-1">*</span>}
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
              {required && <span className="text-red-500 ml-1">*</span>}
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
              {required && <span className="text-red-500 ml-1">*</span>}
            </Label>
          </div>
        );
      
      case 'json':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Textarea
              id={key}
              value={typeof value === 'object' ? JSON.stringify(value, null, 2) : value}
              onChange={(e) => {
                try {
                  const jsonValue = JSON.parse(e.target.value);
                  handleChange(key, jsonValue);
                } catch {
                  handleChange(key, e.target.value);
                }
              }}
              placeholder={placeholder || "Enter valid JSON"}
              disabled={disabled}
              required={required}
            />
          </div>
        );
      
      case 'tags':
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={key}
              value={Array.isArray(value) ? value.join(', ') : value}
              onChange={(e) => {
                const tagsArray = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
                handleChange(key, tagsArray);
              }}
              placeholder={placeholder || "Enter comma-separated values"}
              disabled={disabled}
              required={required}
            />
          </div>
        );
      
      default:
        return (
          <div className="space-y-2" key={key}>
            <Label htmlFor={key}>
              {label}
              {required && <span className="text-red-500 ml-1">*</span>}
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
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {authSchema.map(renderField)}
    </div>
  );
} 