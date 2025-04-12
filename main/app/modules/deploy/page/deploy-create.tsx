"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Github, ArrowLeft, AlertCircle } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { fetchRepositoryMeta, checkMcpExists } from "../api/api.deploy";
import { McpRegistry } from "../components/deploy-create/mcp-registry";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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
  const [includeInTools, setIncludeInTools] = useState(true);
  const [makePublic, setMakePublic] = useState(true);
  const [repoName, setRepoName] = useState("");
  const [repoDescription, setRepoDescription] = useState("");
  const [mcpExists, setMcpExists] = useState(false);

  const handleFetch = async () => {
    if (!githubUrl) return;
    setIsFetching(true);
    setError(null);
    setMcpExists(false);

    try {
      // Сначала получаем метаданные репозитория
      const response = await fetchRepositoryMeta(githubUrl);
      console.log('Response from API:', response);
      
      // Затем проверяем существование MCP (чтобы уведомление появилось только после завершения запроса)
      const exists = await checkMcpExists(githubUrl);
      setMcpExists(exists);
      
      if (response && response.env_variables) {
        const transformedVars = Object.entries(response.env_variables).map(([name, value]) => ({
          name,
          value: value || "",
          required: true
        }));
        
        setEnvVars(transformedVars);
        setIsFetched(true);
        
        if (response.name) setRepoName(response.name);
        if (response.description) setRepoDescription(response.description);
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

    try {
      // Здесь будет API вызов для деплоя
      console.log('Deploying with env vars:', envVars);
      console.log('Include in VeyraX tools:', includeInTools);
      console.log('Make public:', makePublic);
      
      // Подготовка данных для отправки
      const deployData = {
        repo_url: githubUrl,
        env_variables: Object.fromEntries(envVars.map(env => [env.name, env.value])),
        include_in_tools: includeInTools,
        is_public: makePublic,
        name: repoName,
        description: repoDescription
      };
      
      console.log('Deploy data:', deployData);
      
      setTimeout(() => {
        router.push("/deployment");
        setIsLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error during deployment:', error);
      setIsLoading(false);
    }
  };

  const updateEnvVar = (index: number, value: string) => {
    const updated = [...envVars];
    updated[index] = { ...updated[index], value };
    setEnvVars(updated);
  };

  const isEnvVarsValid = () => {
    return envVars.every(env => !env.required || env.value.trim() !== "");
  };

  const handleGoToExistingMcp = () => {
    // В будущем здесь будет переход на страницу существующего MCP
    router.push("/deployment");
  };

  const handleSelectRepository = (repoUrl: string) => {
    setGithubUrl(repoUrl);
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
                <Loader2 className="h-4 w-4 animate-spin" />
              </>
            ) : "Fetch"}
          </Button>
        </div>
        
        {error && (
          <div className="mt-2 text-sm text-red-500">
            {error}
          </div>
        )}

        {isFetched && mcpExists && (
          <Alert className="mt-4 border-amber-500 bg-amber-50 dark:border-amber-800 dark:bg-amber-900/20 p-0 flex items-center">
            <div className="flex items-center w-full">
              <div className="flex-shrink-0 pl-4">
                <AlertCircle className="h-4 w-4 text-amber-500 dark:text-amber-400" />
              </div>
              <div className="flex-grow p-4">
                <AlertTitle className="text-amber-700 dark:text-amber-400">This MCP has been deployed.</AlertTitle>
                <AlertDescription className="text-amber-600 dark:text-amber-400">
                  You can simply connect it. 
                </AlertDescription>
              </div>
              <div className="flex-shrink-0 self-stretch flex items-center pr-4">
                <Button 
                  variant="outline" 
                  className="border-amber-500 text-amber-600 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-400 dark:hover:bg-amber-900/30"
                  onClick={handleGoToExistingMcp}
                >
                  Connect to existing MCP
                </Button>
              </div>
            </div>
          </Alert>
        )}

        {isFetched ? (
          <>
            <div className="mt-6 space-y-6">
              <div>
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-32 text-sm font-medium text-muted-foreground">
                      Name
                    </div>
                    <div className="flex-1">
                      <Input
                        value={repoName}
                        disabled={true}
                        placeholder="Repository Name"
                        className="h-9 text-sm bg-muted"
                      />
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-32 text-sm font-medium text-muted-foreground pt-2">
                      Description
                    </div>
                    <div className="flex-1">
                      <Textarea
                        value={repoDescription}
                        disabled={true}
                        placeholder="Repository Description"
                        className="min-h-[80px] text-sm bg-muted"
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h2 className="text-xl font-medium mb-4">Environment Variables</h2>
                <div className="space-y-3">
                  {envVars.map((env, index) => (
                    <div key={env.name} className="flex items-center gap-4">
                      <div className="w-64 text-sm font-mono text-muted-foreground truncate">
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
              </div>
        
            </div>
            
            <div className="flex justify-between mt-6">
              <Button 
                onClick={() => {
                  setIsFetched(false);
                  setEnvVars([]);
                  setError(null);
                  setGithubUrl("");
                  setRepoName("");
                  setRepoDescription("");
                  setMcpExists(false);
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
                    <Loader2 className="h-4 w-4 animate-spin" />
                  </>
                ) : "Deploy"}
              </Button>
            </div>
          </>
        ) : (
          <McpRegistry onSelect={handleSelectRepository} />
        )}
      </div>
    </div>
  );
}
