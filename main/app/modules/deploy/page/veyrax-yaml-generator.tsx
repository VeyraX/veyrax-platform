"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Loader2, Github, FileText, Download, Copy, CheckIcon } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { generateVeyraxYaml } from "../api/api.deploy";
import { toast } from "sonner";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export default function VeyraxYamlGeneratorPage() {
  const [githubUrl, setGithubUrl] = useState<string>("");
  const [generatedYaml, setGeneratedYaml] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!githubUrl) {
      setError("Please enter a GitHub repository URL");
      return;
    }

    setError(null);
    setIsGenerating(true);
    setGeneratedYaml("");

    try {
      const result = await generateVeyraxYaml(githubUrl);
      
      if (result.success) {
        setGeneratedYaml(result.veyrax_yaml);
      } else {
        throw new Error(result.message || "Failed to generate veyrax.yaml");
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
      toast.error("Failed to generate veyrax.yaml");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    if (!generatedYaml) return;
    
    navigator.clipboard.writeText(generatedYaml);
    setCopied(true);
    
    setTimeout(() => {
      setCopied(false);
    }, 2000);
  };

  const handleDownload = () => {
    if (!generatedYaml) return;
    
    const blob = new Blob([generatedYaml], { type: "text/yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "veyrax.yaml";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col items-start justify-center min-h-screen max-w-4xl mx-auto px-4 w-full py-12 space-y-8">
      <div className="flex flex-col items-start space-y-2">
        <Badge className="text-xs bg-primary text-primary-foreground rounded-full">
          Beta
        </Badge>
        <h1 className="text-4xl font-medium text-foreground">
          veyrax.yaml Generator
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
              placeholder="https://github.com/username/repository"
              className="pl-10 h-10"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              disabled={isGenerating}
            />
          </div>
          <Button 
            variant="default" 
            onClick={handleGenerate} 
            disabled={isGenerating || !githubUrl}
            className="gap-1 min-w-[90px] h-10"
          >
            {isGenerating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : "Generate"}
          </Button>
        </div>
        
        {error && (
          <div className="mt-2 text-sm text-red-500">
            {error}
          </div>
        )}

        {generatedYaml && (
          <div className="mt-6 space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <div className="text-sm font-medium text-foreground">veyrax.yaml</div>
                <div className="flex gap-2">
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button 
                          onClick={handleDownload}
                          className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                          aria-label="Download YAML"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Download as file</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>

                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button 
                          onClick={handleCopy}
                          className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                          aria-label="Copy YAML"
                        >
                          {copied ? (
                            <CheckIcon className="h-4 w-4 text-green-500" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Copy to clipboard</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>

                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Link 
                          href="https://docs.veyrax.com/deployment/deploy" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-foreground transition-colors p-1 rounded-md hover:bg-accent"
                        >
                          <FileText className="h-4 w-4" />
                        </Link>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>View documentation</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
              <div className="rounded-md overflow-hidden">
                <SyntaxHighlighter 
                  language="yaml" 
                  style={vscDarkPlus}
                  customStyle={{ margin: 0, borderRadius: '0.375rem' }}
                >
                  {generatedYaml}
                </SyntaxHighlighter>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
