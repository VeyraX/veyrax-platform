import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { McpDetails, McpDeployment, EnvVariable } from "../../api/types.integrations.mcp";
import { createClient } from "@/lib/utils/supabase/client";

const supabase = createClient();

interface McpSettingsProps {
  mcpId: string;
  mcpDetails: McpDetails | null;
  deployments?: McpDeployment[];
}

export function McpSettings({ mcpId, mcpDetails, deployments = [] }: McpSettingsProps) {
  const [name, setName] = useState<string>("");
  const [description, setDescription] = useState<string>("");
  const [envVariables, setEnvVariables] = useState<EnvVariable[]>([]);

  useEffect(() => {
    if (mcpDetails) {
      setName(mcpDetails.name || "");
      setDescription(mcpDetails.description || "");
      
      // Convert env object to array of key-value pairs
      if (mcpDetails.env) {
        const envArray = Object.entries(mcpDetails.env).map(([key, value]) => ({
          key,
          value: value as string
        }));
        setEnvVariables(envArray);
      }
    }
  }, [mcpDetails]);

  return (
    <div className="space-y-6">
      {/* Basic Information Panel */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm font-medium text-muted-foreground">
              Repository Name
            </div>
            <div className="flex-1">
              <Input
                value={name}
                readOnly
                className="h-9 text-sm"
                disabled={true}
              />
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-32 text-sm font-medium text-muted-foreground pt-2">
              Description
            </div>
            <div className="flex-1">
              <Textarea
                value={description}
                readOnly
                className="min-h-[80px] text-sm"
                disabled={true}
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Environment Variables Panel */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-medium text-foreground">Environment Variables</h2>
        </div>

        <div className="space-y-4">
          {envVariables.length > 0 ? (
            <div className="space-y-3">
              {envVariables.map((env, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="flex-1">
                    <Input
                      value={env.key}
                      readOnly
                      className="h-9 text-sm"
                      disabled={true}
                    />
                  </div>
                  <div className="flex-1">
                    <Input
                      value={env.value}
                      readOnly
                      type="password"
                      className="h-9 text-sm"
                      disabled={true}
                    />
                  </div>
                  <div className="h-9 w-9 flex items-center justify-center">
                    
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-4 text-center text-muted-foreground">
              <p>No environment variables configured.</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Deployment Settings Panel */}
      <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-medium text-foreground">Deployment Settings</h2>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm font-medium text-muted-foreground">
              Commit Hash
            </div>
            <div className="flex-1">
              <Input
                value={mcpDetails?.last_commit_hash || ""}
                readOnly
                className="h-9 text-sm"
                disabled={true}
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm font-medium text-muted-foreground">
              Repository URL
            </div>
            <div className="flex-1">
              <Input
                value={mcpDetails?.repo_url || ""}
                readOnly
                className="h-9 text-sm"
                disabled={true}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
