import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { CustomAuthField } from "../../api/types.integrations";
import { useState, useEffect } from "react";
import { ArrowRight } from "lucide-react";
interface MailAuthFormProps {
  authSchema: CustomAuthField[];
  authData: Record<string, any>;
  onChange: (authData: Record<string, any>) => void;
  disabled?: boolean;
}

export function MailAuthForm({ authSchema, authData, onChange, disabled = false }: MailAuthFormProps) {
  const [showPasswordField, setShowPasswordField] = useState(false);
  
  useEffect(() => {
    setShowPasswordField(false);
  }, []);
  
  useEffect(() => {
    setShowPasswordField(false);
  }, [authData.username]);
  
  const usernameField = authSchema.find(field => field.key === "username");
  const passwordField = authSchema.find(field => field.key === "password");

  useEffect(() => {
    if (passwordField && authData[passwordField.key] && !showPasswordField) {
      setShowPasswordField(true);
    }
  }, [authData, passwordField, showPasswordField]);
  
  const handleChange = (key: string, value: any) => {
    onChange({ ...authData, [key]: value });
  };

  const handleGeneratePassword = () => {
    window.open("https://myaccount.google.com/apppasswords", "_blank");
    
    setTimeout(() => {
      setShowPasswordField(true);
    }, 2000);
  };

  return (
    <div className="grid grid-cols-1 gap-4">
      {usernameField && (
        <div className="space-y-2">
          <Label htmlFor={usernameField.key}>
            Your Email
          </Label>
          <Input
            id={usernameField.key}
            type="email"
            value={authData[usernameField.key] || ''}
            onChange={(e) => handleChange(usernameField.key, e.target.value)}
            placeholder="your.email@gmail.com"
            disabled={disabled}
            required={usernameField.required}
          />
        </div>
      )}
      
      {!showPasswordField && (
        <Button 
          onClick={handleGeneratePassword}
          disabled={disabled}
          variant="outline"
          className="mt-2"
        >
          Generate App Password
          <ArrowRight className="w-4 h-4" />
        </Button>
      )}
      
      {showPasswordField && passwordField && (
        <div 
          className="space-y-2" 
          style={{ 
            animation: "fadeIn 0.5s ease-in-out",
          }}
        >
          <Label htmlFor={passwordField.key}>
            App Password
          </Label>
          <Input
            id={passwordField.key}
            type="password"
            value={authData[passwordField.key] || ''}
            onChange={(e) => handleChange(passwordField.key, e.target.value)}
            placeholder="16-character app password"
            disabled={disabled}
            required={passwordField.required}
          />
          <style jsx>{`
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }
          `}</style>
        </div>
      )}
    </div>
  );
} 