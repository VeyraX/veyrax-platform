"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Code, Github, Terminal, Upload } from "lucide-react";
import { dummyTools, dummyInstallCommands, dummyMetrics, dummyMcpInfo } from "../api/deploy-view-dummy-data";
import { Tool } from "../api/types.deploy";

interface DeployViewPageProps {
  mcpId?: string;
  repoName?: string;
  githubUrl?: string;
  imageName?: string;
}

export default function DeployViewPage({ 
  mcpId = dummyMcpInfo.id, 
  repoName = dummyMcpInfo.repoName, 
  githubUrl = dummyMcpInfo.githubUrl,
  imageName = "VeyraX MCP Client"
}: DeployViewPageProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [deploymentStatus, setDeploymentStatus] = useState<'Active' | 'Inactive'>('Active');
  const [tools, setTools] = useState<Tool[]>([]);
  const [activeInstallTab, setActiveInstallTab] = useState<'npm' | 'yarn' | 'pnpm'>('npm');
  
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const tabParam = searchParams.get('tab');
    
    if (tabParam === 'api') {
      setActiveTab('api');
    } else if (tabParam === 'deployment') {
      setActiveTab('deployment');
    } else if (tabParam === 'settings') {
      setActiveTab('settings');
    } else if (tabParam === 'overview' || !tabParam) {
      setActiveTab('overview');
    }
    
    // Simulate loading data
    const timer = setTimeout(() => {
      setTools(dummyTools);
      setIsLoading(false);
    }, 800);
    
    return () => clearTimeout(timer);
  }, [mcpId]);
  
  const handleBack = () => {
    router.back();
  };
  
  if (isLoading) {
    return (
      <div className="h-screen overflow-hidden flex flex-col">
        <div className="flex items-center justify-between w-full px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <Skeleton className="w-6 h-6 rounded-full" />
            <Skeleton className="w-40 h-5" />
          </div>
          <Skeleton className="w-20 h-7 rounded-full" />
        </div>
        
        <div className="flex-1 overflow-hidden p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <Skeleton className="w-full h-40" />
              </div>
              
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-24 h-6" />
                <Skeleton className="w-full h-20" />
              </div>
            </div>
            
            <div className="flex flex-col space-y-6">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                <Skeleton className="w-32 h-6" />
                <div className="space-y-3">
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                  <Skeleton className="w-full h-16" />
                </div>
              </div>

              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Skeleton className="w-32 h-6" />
                    <Skeleton className="w-8 h-8 rounded-full" />
                  </div>
                  <Skeleton className="w-full h-40" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between w-full px-4 py-2 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <button onClick={handleBack} className="text-gray-700 dark:text-gray-300 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
            <ArrowLeft size={16} />
          </button>
          <div className="flex items-center text-sm">
            <span className="font-medium text-gray-900 dark:text-gray-100">{repoName}</span>
            <div className="ml-2 px-2 py-0.5 text-xs rounded-full bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300">
              {deploymentStatus}
            </div>
          </div>
        </div>
        
        {/* Right side of the header */}
        <div className="flex items-center gap-2">
          <Button 
            size="sm"
            variant="outline"
            className="gap-1 rounded-full"
            onClick={() => window.open(githubUrl, '_blank')}
          >
            <span>Publish</span>
          </Button>
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="w-full px-6 py-6">
          <Tabs 
            defaultValue="overview" 
            className="w-full"
            value={activeTab}
            onValueChange={(value) => {
              setActiveTab(value);
              // Update URL query parameter when tab changes
              const url = new URL(window.location.href);
              url.searchParams.set('tab', value);
              window.history.pushState({}, '', url);
            }}
          >
            <div className="mb-6 flex justify-between">
              {/* Left tabs */}
              <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="overview"
                >
                  Overview
                </TabsTrigger>
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="api"
                >
                  API
                </TabsTrigger>
              </TabsList>
              
              {/* Right tabs */}
              <TabsList className="h-auto gap-4 rounded-none bg-transparent px-0 py-0 text-foreground">
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="deployment"
                >
                  Deployment
                </TabsTrigger>
                <TabsTrigger 
                  className="relative after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5 hover:bg-accent hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:after:bg-primary data-[state=active]:hover:bg-accent" 
                  value="settings"
                >
                  Settings
                </TabsTrigger>
              </TabsList>
            </div>

            {/* Tab Content */}
            <TabsContent value="overview" className="mt-0">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-6">
                  {/* Overview Panel */}
                  <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <div className="flex flex-col">
                      <h2 className="text-xl font-medium text-foreground">{repoName}</h2>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm text-muted-foreground">{imageName}</span>
                        <a href={githubUrl} target="_blank" rel="noopener noreferrer" 
                          className="text-blue-600 dark:text-blue-400 hover:text-blue-800">
                          <Github size={14} />
                        </a>
                      </div>
                    </div>
                    
                    {/* GitHub Stats - Minimal cards */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
                        247 stars
                      </div>
                      
                      <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
                        Published {dummyMetrics.published}
                      </div>
                      
                      <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
                        John Doe
                      </div>
                      
                      <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-md px-2 py-1 text-xs">
                        {dummyMetrics.license}
                      </div>
                    </div>
                    
                    <div className="text-foreground/90">
                      <p>Execute terminal commands and manage files with diff editing capabilities. Coding, shell and terminal, task automation</p>
                      
                      <div className="mt-4">
                        <div className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-800">
                          <span className="text-muted-foreground">MCP ID</span>
                          <span className="font-medium">{mcpId}</span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-100 dark:border-gray-800">
                          <span className="text-muted-foreground">Status</span>
                          <span className="font-medium">{deploymentStatus}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Tools Panel */}
                  <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <div className="flex items-center gap-2">
                      <Terminal size={16} className="text-muted-foreground" />
                      <h2 className="text-xl font-medium text-foreground">Tools</h2>
                    </div>
                    <div className="space-y-4">
                      {tools.map((tool) => (
                        <div key={tool.id} className="bg-gray-50 dark:bg-gray-900/60 border border-gray-100 dark:border-gray-800 rounded-md p-4">
                          <h3 className="font-medium text-foreground mb-1">{tool.name}</h3>
                          <p className="text-muted-foreground text-sm">{tool.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {/* Installation Panel */}
                  <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6 space-y-4">
                    <h2 className="text-xl font-medium text-foreground">Installation</h2>
                    <p className="text-muted-foreground">Run the following command to install:</p>
                    
                    <div className="mt-4">
                      <Tabs 
                        defaultValue="npm" 
                        value={activeInstallTab}
                        onValueChange={(value) => setActiveInstallTab(value as 'npm' | 'yarn' | 'pnpm')}
                        className="w-full"
                      >
                        <TabsList className="grid w-full grid-cols-3 mb-2">
                          <TabsTrigger value="npm">npm</TabsTrigger>
                          <TabsTrigger value="yarn">yarn</TabsTrigger>
                          <TabsTrigger value="pnpm">pnpm</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="npm" className="mt-0">
                          <div className="relative">
                            <div className="bg-gray-950 text-gray-100 p-3 rounded-md font-mono text-sm overflow-x-auto">
                              {dummyInstallCommands.npm}
                            </div>
                            <button 
                              className="absolute top-2 right-2 p-1 bg-gray-800 hover:bg-gray-700 rounded"
                              onClick={() => navigator.clipboard.writeText(dummyInstallCommands.npm)}
                            >
                              <Code size={14} className="text-gray-300" />
                            </button>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="yarn" className="mt-0">
                          <div className="relative">
                            <div className="bg-gray-950 text-gray-100 p-3 rounded-md font-mono text-sm overflow-x-auto">
                              {dummyInstallCommands.yarn}
                            </div>
                            <button 
                              className="absolute top-2 right-2 p-1 bg-gray-800 hover:bg-gray-700 rounded"
                              onClick={() => navigator.clipboard.writeText(dummyInstallCommands.yarn)}
                            >
                              <Code size={14} className="text-gray-300" />
                            </button>
                          </div>
                        </TabsContent>
                        
                        <TabsContent value="pnpm" className="mt-0">
                          <div className="relative">
                            <div className="bg-gray-950 text-gray-100 p-3 rounded-md font-mono text-sm overflow-x-auto">
                              {dummyInstallCommands.pnpm}
                            </div>
                            <button 
                              className="absolute top-2 right-2 p-1 bg-gray-800 hover:bg-gray-700 rounded"
                              onClick={() => navigator.clipboard.writeText(dummyInstallCommands.pnpm)}
                            >
                              <Code size={14} className="text-gray-300" />
                            </button>
                          </div>
                        </TabsContent>
                      </Tabs>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                      <h3 className="font-medium mb-2">Available Platforms</h3>
                      <div className="flex space-x-2">
                        <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1 text-xs">
                          <span className="mr-1">☑️</span> Claude
                        </div>
                        <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1 text-xs">
                          <span className="mr-1">☑️</span> Cursor
                        </div>
                        <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1 text-xs">
                          <span className="mr-1">☑️</span> Windsurf
                        </div>
                        <div className="inline-flex items-center bg-gray-100 dark:bg-gray-800 rounded-full px-3 py-1 text-xs">
                          <span className="mr-1">☑️</span> Vsc
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="api" className="mt-0">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-xl font-medium text-foreground mb-4">API Documentation</h2>
                <div className="text-muted-foreground">
                  API documentation will be displayed here.
                </div>
              </div>
            </TabsContent>

            <TabsContent value="deployment" className="mt-0">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-xl font-medium text-foreground mb-4">Deployment Configuration</h2>
                <div className="text-muted-foreground">
                  Deployment configuration options will appear here.
                </div>
              </div>
            </TabsContent>

            <TabsContent value="settings" className="mt-0">
              <div className="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-6">
                <h2 className="text-xl font-medium text-foreground mb-4">Settings</h2>
                <div className="text-muted-foreground">
                  Deployment settings will appear here.
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
