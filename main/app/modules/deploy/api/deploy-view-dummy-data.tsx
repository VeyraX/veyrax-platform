import { Tool } from "./types.deploy";

export interface InspirationItem {
  name: string;
  url: string;
}

export const dummyTools: Tool[] = [
  {
    id: "execute_command",
    name: "execute_command",
    description: "Execute a terminal command with timeout. Command will continue running in background if it doesn't complete within timeout."
  },
  {
    id: "read_output",
    name: "read_output",
    description: "Read new output from a running terminal session."
  },
  {
    id: "force_terminate",
    name: "force_terminate",
    description: "Force terminate a running terminal session."
  },
  {
    id: "list_sessions",
    name: "list_sessions",
    description: "List all active terminal sessions."
  }
];

export const inspirationItems: InspirationItem[] = [
  {
    name: "Smithery MCP",
    url: "https://github.com/smithery/mcp-core"
  },
  {
    name: "Pulse MCP",
    url: "https://github.com/pulse/mcp-plugin"
  },
  {
    name: "Awesome MCP",
    url: "https://github.com/awesome/mcp-collection"
  },
  {
    name: "DevTools MCP",
    url: "https://github.com/devtools/mcp"
  },
  {
    name: "Terminal MCP",
    url: "https://github.com/terminal/mcp-tools"
  },
  {
    name: "Cloud MCP",
    url: "https://github.com/cloud/mcp-deploy"
  },
  {
    name: "Database MCP",
    url: "https://github.com/db/mcp-connector"
  },
  {
    name: "AI Vision MCP",
    url: "https://github.com/vision/mcp-ai"
  }
];

export const dummyInstallCommands = {
  npm: "npm install @veyrax/mcp-client",
  yarn: "yarn add @veyrax/mcp-client",
  pnpm: "pnpm add @veyrax/mcp-client"
};

export const dummyMetrics = {
  monthlyToolCalls: "403,490",
  license: "MIT",
  local: "Yes",
  published: "1/10/2025"
};

export const dummyMcpInfo = {
  id: "mcp-12345",
  repoName: "veyrax-mcp-example",
  githubUrl: "https://github.com/veyrax/veyrax-mcp-example",
  status: "Active"
};
