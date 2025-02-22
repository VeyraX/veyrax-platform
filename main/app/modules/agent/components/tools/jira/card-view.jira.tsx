import type React from "react";
import { formatDistanceToNow } from "date-fns";
import { ToolCard, ToolCardSkeleton } from "../common/tool-card";
import { Table, TableHeader, TableBody, TableCell, TableRow, TableHead } from "@/components/ui/table";
import type { 
  Issue, 
  Project, 
  Status, 
  Priority, 
  IssueType,
  Field,
  JiraUser
} from "./types.jira";

export function JiraIssueCard({ 
  summary, 
  status, 
  priority, 
  assignee, 
  created,
  url
}: Issue) {

  const statusText = status?.name || 'No status';
  const priorityText = priority?.name || 'No priority';
  const assigneeText = assignee?.displayName || 'Unassigned';
  
  const formattedDate = (() => {
    try {
      const date = new Date(created);
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      return formatDistanceToNow(date, { addSuffix: true });
    } catch {
      return 'Invalid date';
    }
  })();

  const subtitle = [
    statusText,
    priorityText,
    assigneeText,
  ].join(' • ');

  return (
    <ToolCard
      resourceType="jira/issue"
      title={summary}
      subtitle={subtitle}
      externalLink={url}
    />
  );
}

export function JiraProjectList({ projects }: { projects: Project[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Project Name</TableHead>
          <TableHead>Key</TableHead>
          <TableHead>Lead</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {projects.map((project) => (
          <TableRow key={project.id}>
            <TableCell>{project.name}</TableCell>
            <TableCell>{project.key}</TableCell>
            <TableCell>{project.lead?.name || 'No lead'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraStatusList({ statuses }: { statuses: Status[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Category</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {statuses.map((status) => (
          <TableRow key={status.id}>
            <TableCell>{status.name}</TableCell>
            <TableCell>{status.statusCategory?.name || 'No category'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraPriorityList({ priorities }: { priorities: Priority[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Priority</TableHead>
          <TableHead>Description</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {priorities.map((priority) => (
          <TableRow key={priority.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                {priority.iconUrl && (
                  <img src={priority.iconUrl} alt="" className="w-4 h-4" />
                )}
                {priority.name}
              </div>
            </TableCell>
            <TableCell>{priority.description || 'No description'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraIssueTypeList({ issueTypes }: { issueTypes: IssueType[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Type</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Subtask</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {issueTypes.map((type) => (
          <TableRow key={type.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                {type.iconUrl && (
                  <img src={type.iconUrl} alt="" className="w-4 h-4" />
                )}
                {type.name}
              </div>
            </TableCell>
            <TableCell>{type.description || 'No description'}</TableCell>
            <TableCell>{type.subtask ? 'Yes' : 'No'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraFieldList({ fields }: { fields: Field[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Field Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Custom</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {fields.map((field) => (
          <TableRow key={field.id}>
            <TableCell>{field.name}</TableCell>
            <TableCell>{field.schema?.type || 'N/A'}</TableCell>
            <TableCell>{field.custom ? 'Yes' : 'No'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraUserList({ users }: { users: JiraUser[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>User</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.accountId}>
            <TableCell>{user.displayName || 'Unknown'}</TableCell>
            <TableCell>{user.email || 'No email'}</TableCell>
            <TableCell>{user.active ? 'Active' : 'Inactive'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}


export function JiraIssueCardSkeleton() {
  return <ToolCardSkeleton />;
}

export function JiraProjectListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Project Name</TableHead>
          <TableHead>Key</TableHead>
          <TableHead>Lead</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-16 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraStatusListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Category</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraPriorityListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Priority</TableHead>
          <TableHead>Description</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-40 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraIssueTypeListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Type</TableHead>
          <TableHead>Description</TableHead>
          <TableHead>Subtask</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-40 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-16 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraFieldListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Field Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Custom</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-16 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function JiraUserListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>User</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-40 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-16 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}