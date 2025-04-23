"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Github, ArrowLeft, FileText } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { fetchRepositoryMeta, checkMcpExists, deployMcpRepository, updateMcpImageName } from "../api/api.deploy";
import { McpRegistry } from "../components/deploy-create/mcp-registry";
import { toast } from "sonner";
import { ExistingMcpCard } from "../components/deploy-create/mcp-card-existing-repo";
import { Badge } from "@/components/ui/badge";

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
  const [noDockerfileError, setNoDockerfileError] = useState<boolean>(false);
  const [repoName, setRepoName] = useState("");
  const [repoDescription, setRepoDescription] = useState("");
  const [mcpExists, setMcpExists] = useState(false);
  const [repositoryId, setRepositoryId] = useState<string | null>(null);
  const [commitHash, setCommitHash] = useState<string | null>(null);
  const [ownerName, setOwnerName] = useState<string>("");
  const [resetKey, setResetKey] = useState<number>(0);
  const [existingMcpData, setExistingMcpData] = useState<{
    is_approved: boolean;
    image_name: string;
    env: Record<string, string>;
  } | null>(null);
  const [isGithubUrl, setIsGithubUrl] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  const handleFetch = async () => {
    if (!githubUrl) return;
    setIsFetching(true);
    setError(null);
    setMcpExists(false);
    setExistingMcpData(null);
    setNoDockerfileError(false);

    try {
      const response = await fetchRepositoryMeta(githubUrl);
      console.log('Response from API:', response);
      
      if (response.dockerfile_exists === false) {
        setNoDockerfileError(true);
      }
      
      const mcpCheck = await checkMcpExists(githubUrl);
      
      if (typeof mcpCheck !== 'boolean' && mcpCheck.exists) {
        setMcpExists(true);
        
        if (mcpCheck.dockerfile_exists === false) {
          setNoDockerfileError(true);
        }
        
        if (response.is_approved && response.image_name) {
          setExistingMcpData({
            is_approved: response.is_approved,
            image_name: response.image_name,
            env: response.env_variables || {}
          });
        } else if (mcpCheck.is_approved && mcpCheck.image_name) {
          setExistingMcpData({
            is_approved: mcpCheck.is_approved,
            image_name: mcpCheck.image_name,
            env: mcpCheck.env
          });
        }
      }
      
      if (response && response.env_variables) {
        const transformedVars = Object.entries(response.env_variables).map(([name, value]) => ({
          name,
          value: value || "",
          required: true
        }));
        
        setEnvVars(transformedVars);
        setIsFetched(true);
        
        setRepoName(response.name || "");
        setRepoDescription(response.description || "");
        setRepositoryId(response.repository_id || null);
        setCommitHash(response.last_commit_hash || null);
        setOwnerName(response.owner || "");
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
    if (!repositoryId) {
      setError("Repository ID is missing. Please try fetching the repository again.");
      return;
    }
    
    setIsLoading(true);
    setError(null);

    try {
      const envVariablesObj = Object.fromEntries(
        envVars.map(env => [env.name, env.value])
      );
      
      const imageName = (repoName.toLowerCase().replace(/[^a-z0-9-]/g, '-') || 'default') + 
        (ownerName ? `-${ownerName.toLowerCase().replace(/[^a-z0-9-]/g, '-')}` : '') + 
        '-mcp-server';
      
      await updateMcpImageName(repositoryId, imageName);
      
      
      try {
        await deployMcpRepository(
          githubUrl,
          imageName,
          repositoryId,
          commitHash || undefined,
          envVariablesObj
        );
        
        router.push(`/integrations/mcp/${imageName}?tab=deployment`);
      } catch (deployError) {
        console.error('Deployment error:', deployError);
        toast.error("Deployment initiated but encountered an issue. You can view status in the MCP page.");
        router.push(`/integrations/mcp/${imageName}?tab=deployment`);
      }
    } catch (error) {
      console.error('Error during deployment process:', error);
      setError(error instanceof Error ? error.message : "An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  const updateEnvVar = (index: number, value: string) => {
    const updated = [...envVars];
    updated[index] = { ...updated[index], value };
    setEnvVars(updated);
  };

  const isEnvVarsValid = () => {
    return true;
  };

  const handleGoToExistingMcp = () => {
    router.push("/deployment");
  };

  const handleSelectRepository = (repoUrl: string) => {
    setGithubUrl(repoUrl);
    setIsGithubUrl(true);
  };

  const handleGithubUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const url = e.target.value;
    setGithubUrl(url);

    const isValidGithubUrl = url.startsWith("https://github.com/") && 
                             url.includes("/", "https://github.com/".length);
    
    setIsGithubUrl(isValidGithubUrl);
    
    if (!isValidGithubUrl) {
      setSearchQuery(url);
    } else {
      setSearchQuery("");
    }
  };

  return (
    <div className="flex flex-col items-start justify-center min-h-screen max-w-4xl mx-auto px-4 w-full py-12 space-y-8">
      <div className="flex flex-col items-start space-y-2">
        <Badge className="text-xs bg-primary text-primary-foreground rounded-full">
          Beta
        </Badge>
        <h1 className="text-4xl font-medium text-foreground">
          Deploy MCP Server
        </h1>
        <div className="flex items-center gap-2">
          <p className="text-xl text-muted-foreground font-normal">
            Enter a GitHub repository URL to get started
          </p>
          <Link 
            href="https://docs.veyrax.com/deployment/deploy" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-primary transition-colors"
            title="Documentation"
          >
            <FileText size={12} />
          </Link>
        </div>
      </div>

      <div className="w-full space-y-6">
        <div className="flex gap-3">
          <div className="relative flex-grow">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <Github className="h-5 w-5 text-muted-foreground" />
            </div>
            <Input
              type="text"
              placeholder="https://github.com/username/repository or search by name"
              className="pl-10 h-10 pr-10"
              value={githubUrl}
              onChange={handleGithubUrlChange}
              disabled={isFetching || isFetched}
            />
            {isSearching && !isGithubUrl && !isFetched && (
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            )}
          </div>
          <Button 
            variant="default" 
            onClick={handleFetch} 
            disabled={!githubUrl || isFetching || isLoading || isFetched || !isGithubUrl}
            className="gap-1 min-w-[90px] h-10"
          >
            {isFetching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : "Fetch"}
          </Button>
        </div>
        
        {error && !noDockerfileError && (
          <div className="mt-2 text-sm text-red-500">
            {error}
          </div>
        )}

        {noDockerfileError && (
          <div className="mt-6 p-4 border border-yellow-300 bg-yellow-50 dark:bg-yellow-950/30 dark:border-yellow-700/50 rounded-lg">
            <h3 className="text-lg font-medium text-yellow-800 dark:text-yellow-300 mb-2">
              Missing Dockerfile
            </h3>
            <p className="text-sm text-yellow-700 dark:text-yellow-400 mb-3">
              We couldn't find a Dockerfile in your repository. Dockerfile is very important for MCP deployment. Continuing without a Dockerfile may cause deployment issues.
            </p>
            <div className="flex gap-2">
              <Button 
                onClick={() => {
                  setIsFetched(false);
                  setEnvVars([]);
                  setError(null);
                  setGithubUrl("");
                  setRepoName("");
                  setRepoDescription("");
                  setMcpExists(false);
                  setExistingMcpData(null);
                  setNoDockerfileError(false);
                  setRepositoryId(null);
                  setCommitHash(null);
                  setOwnerName("");
                  setSearchQuery("");
                  setSearchResults([]);
                  setIsSearching(false);
                  setIsGithubUrl(false);
                  setResetKey(prevKey => prevKey + 1);
                }}
                variant="outline"
                className="mt-2 text-xs h-8"
              >
                Try another repository
              </Button>
              <Button 
                onClick={() => {
                  setNoDockerfileError(false);
                }}
                variant="default"
                className="mt-2 text-xs h-8"
              >
                Try Anyway
              </Button>
            </div>
          </div>
        )}

        {isFetched && mcpExists && existingMcpData?.is_approved && (
          <div className="mt-6">
            <ExistingMcpCard 
              repoUrl={githubUrl}
              imageName={existingMcpData.image_name}
              repositoryId={repositoryId || ''}
              repoName={repoName}
              repoDescription={repoDescription}
              env={existingMcpData.env}
              onBack={() => {
                setIsFetched(false);
                setEnvVars([]);
                setError(null);
                setGithubUrl("");
                setRepoName("");
                setRepoDescription("");
                setMcpExists(false);
                setExistingMcpData(null);
                setNoDockerfileError(false);
                setRepositoryId(null);
                setCommitHash(null);
                setOwnerName("");
                setSearchQuery("");
                setSearchResults([]);
                setIsSearching(false);
                setIsGithubUrl(false);
                setResetKey(prevKey => prevKey + 1);
              }}
            />
          </div>
        )}

        {isFetched && (!mcpExists || !existingMcpData?.is_approved) ? (
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
                {envVars.length > 0 ? (
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
                ) : (
                  <div className="text-muted-foreground">We didn't find any environment variables for this MCP. You can proceed with the deployment.</div>
                )}
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
                  setExistingMcpData(null);
                  setNoDockerfileError(false);
                  setRepositoryId(null);
                  setCommitHash(null);
                  setOwnerName("");
                  setSearchQuery("");
                  setSearchResults([]);
                  setIsSearching(false);
                  setIsGithubUrl(false);
                  setResetKey(prevKey => prevKey + 1);
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
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : "Deploy"}
              </Button>
            </div>
          </>
        ) : null}

        {!isFetched && (
          <McpRegistry 
            key={resetKey}
            onSelect={handleSelectRepository} 
            externalSearchQuery={searchQuery}
            onSearchStateChange={(searching) => setIsSearching(searching)}
          />
        )}
      </div>
    </div>
  );
}
