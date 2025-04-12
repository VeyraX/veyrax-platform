"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Github, ArrowLeft } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { fetchEnvironmentVariables } from "../api/api.deploy";
import { McpRegistry } from "../components/deploy-create/mcp-registry";

interface EnvVar {
  name: string;
  value: string;
  required: boolean;
}

export default function DeployCreatePage() {
  const router = useRouter();
  const [githubUrl, setGithubUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [envVars, setEnvVars] = useState<EnvVar[]>([]);
  const [isFetched, setIsFetched] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetch = async () => {
    if (!githubUrl) return;
    setIsFetching(true);
    setError(null);

    try {
      const response = await fetchEnvironmentVariables(githubUrl);
      console.log('Response from API:', response);
      
      if (response && response.env_variables) {
        const transformedVars = Object.entries(response.env_variables).map(([name, value]) => ({
          name,
          value: value || "",
          required: true
        }));
        
        setEnvVars(transformedVars);
        setIsFetched(true);
      } else {
        setError("No environment variables found");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch environment variables";
      setError(errorMessage);
      console.error("Error fetching environment variables:", err);
    } finally {
      setIsFetching(false);
    }
  };

  const handleDeploy = async () => {
    setIsLoading(true);

    // This would be an actual deployment API call in production
    setTimeout(() => {
      router.push("/deployment");
      setIsLoading(false);
    }, 1500);
  };

  const updateEnvVar = (index: number, value: string) => {
    const updated = [...envVars];
    updated[index] = { ...updated[index], value };
    setEnvVars(updated);
  };

  const isEnvVarsValid = () => {
    return envVars.every(env => !env.required || env.value.trim() !== "");
  };

  return (
    <div className="flex flex-col items-start justify-center min-h-screen max-w-4xl mx-auto px-4 w-full py-12 space-y-8">
      <div className="flex flex-col items-start space-y-2">
        <h1 className="text-4xl font-medium text-foreground">
          Deploy a New MCP Server
        </h1>
        <p className="text-lg text-muted-foreground font-normal">
          Enter a GitHub repository URL to get started
        </p>
      </div>

      <div className="w-full space-y-6">
        <div className="flex gap-3">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <Github className="h-5 w-5 text-muted-foreground" />
            </div>
            <Input
              type="text"
              placeholder="https://github.com/username/repository"
              className="pl-10 h-10"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              disabled={isFetching || isFetched}
            />
          </div>
          <Button 
            variant="default" 
            onClick={handleFetch} 
            disabled={!githubUrl || isFetching || isLoading || isFetched}
            className="gap-1 min-w-[90px] h-10"
          >
            {isFetching ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                <span>Fetching</span>
              </>
            ) : "Fetch"}
          </Button>
        </div>
        
        {error && (
          <div className="mt-2 text-sm text-red-500">
            {error}
          </div>
        )}

        {isFetched ? (
          <>
            <Card className="shadow-none rounded-lg mt-6">
              <CardContent className="p-4 space-y-4">
                <h2 className="text-xl font-medium">Environment Variables</h2>
                
                <div className="space-y-3">
                  {envVars.map((env, index) => (
                    <div key={env.name} className="flex items-center gap-3">
                      <div className="w-32 text-sm font-mono text-muted-foreground">
                        {env.name}
                      </div>
                      <div className="flex-1">
                        <Input
                          value={env.value}
                          onChange={(e) => updateEnvVar(index, e.target.value)}
                          placeholder="Value"
                          className="h-9 text-sm"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <div className="flex justify-between mt-4">
              <Button 
                onClick={() => {
                  setIsFetched(false);
                  setEnvVars([]);
                  setError(null);
                  setGithubUrl("");
                }}
                variant="outline"
                className="px-4 gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              
              <Button 
                onClick={handleDeploy} 
                disabled={isLoading || !isEnvVarsValid()} 
                className="px-6"
                variant="default"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    <span>Deploying...</span>
                  </>
                ) : "Deploy"}
              </Button>
            </div>
          </>
        ) : (
          <McpRegistry />
        )}
      </div>
    </div>
  );
}
