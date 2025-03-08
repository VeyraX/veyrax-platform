import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface DbConfig {
  account: string;
  user: string;
  password: string;
  warehouse: string;
  database: string;
  schema: string;
  role: string;
}

interface SnowflakeConfigFormProps {
  config: any; 
  onChange: (config: any) => void;
  disabled?: boolean;
}

export function SnowflakeConfigForm({ config, onChange, disabled = false }: SnowflakeConfigFormProps) {
  const handleChange = (field: keyof DbConfig, value: string) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="account">Account Identifier</Label>
          <Input
            id="account"
            value={config.account}
            onChange={(e) => handleChange('account', e.target.value)}
            placeholder="e.g., ACCOUNT_IDENTIFIER"
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="warehouse">Warehouse</Label>
          <Input
            id="warehouse"
            value={config.warehouse}
            onChange={(e) => handleChange('warehouse', e.target.value)}
            placeholder="e.g., DATAWAREHOUSE"
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="database">Database</Label>
          <Input
            id="database"
            value={config.database}
            onChange={(e) => handleChange('database', e.target.value)}
            placeholder="e.g., DATABASE_NAME"
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="schema">Schema</Label>
          <Input
            id="schema"
            value={config.schema}
            onChange={(e) => handleChange('schema', e.target.value)}
            placeholder="e.g., PUBLIC"
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="user">Username</Label>
          <Input
            id="user"
            value={config.user}
            onChange={(e) => handleChange('user', e.target.value)}
            placeholder="e.g., USERNAME"
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={config.password}
            onChange={(e) => handleChange('password', e.target.value)}
            placeholder={disabled ? "••••••" : "Enter password"}
            disabled={disabled}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="role">Role (optional)</Label>
          <Input
            id="role"
            value={config.role}
            onChange={(e) => handleChange('role', e.target.value)}
            placeholder="e.g., ROLE_NAME"
            disabled={disabled}
          />
        </div>
      </div>
    </div>
  );
}