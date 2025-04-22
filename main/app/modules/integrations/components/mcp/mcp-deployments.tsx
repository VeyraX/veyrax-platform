import { useState } from "react";
import { format, parseISO } from "date-fns";
import { McpDeployment } from "../../api/types.integrations.mcp";
import { McpDeploymentSheet } from "./mcp-deployment-sheet";
import { Button } from "@/components/ui/button";
import { FileText, Copy, Check } from "lucide-react";

interface McpDeploymentsProps {
  deployments: McpDeployment[];
  repoName: string;
}

export function McpDeployments({ deployments, repoName }: McpDeploymentsProps) {
  const [selectedDeployment, setSelectedDeployment] = useState<McpDeployment | null>(null);
  const [copiedDeploymentId, setCopiedDeploymentId] = useState<string | null>(null);

  const handleCopyHash = (deploymentId: string, hash: string) => {
    navigator.clipboard.writeText(hash);
    setCopiedDeploymentId(deploymentId);
    setTimeout(() => setCopiedDeploymentId(null), 2000);
  };

  return (
    <div className="mt-4">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Deployment ID
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Commit Hash
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
                Date
              </th>
              <th scope="col" className="px-6 py-3 text-left text-sm font-medium">
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {Array.isArray(deployments) && deployments.length > 0 ? (
              deployments.map((deployment) => (
                <tr key={deployment.id}>
                  <td className="px-6 py-4 text-sm font-mono text-gray-900">
                    {deployment.deployment_id || `DEP-${typeof deployment.id === 'string' ? deployment.id.substring(0, 8) : deployment.id}`}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={deployment.status} />
                  </td>
                  <td className="px-6 py-4 text-sm font-mono text-gray-700">
                    {deployment.commit_hash ? (
                      <div className="flex items-center">
                        <span>{deployment.commit_hash.substring(0, 7)}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="ml-2 h-6 w-6 p-0"
                          onClick={() => deployment.commit_hash && handleCopyHash(deployment.id, deployment.commit_hash)}
                        >
                          {copiedDeploymentId === deployment.id ? 
                            <Check className="h-3 w-3" /> : 
                            <Copy className="h-3 w-3" />
                          }
                        </Button>
                      </div>
                    ) : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {deployment.created_at ? format(parseISO(deployment.created_at), 'PPp') : '-'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button
                      onClick={() => setSelectedDeployment(deployment)}
                      variant="outline"
                    >
                      <FileText className="w-4 h-4" />
                      Build Logs
                    </Button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center text-sm">
                  No deployments found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <McpDeploymentSheet
        isOpen={!!selectedDeployment}
        onClose={() => setSelectedDeployment(null)}
        deployment={selectedDeployment!}
      />
    </div>
  );
}

function StatusBadge({ status }: { status: McpDeployment['status'] }) {
  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    building: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    ready: 'bg-green-100 text-green-800',
    'in progress': 'bg-blue-100 text-blue-800',
    started: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
