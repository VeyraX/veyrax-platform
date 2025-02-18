import type React from "react"
import type { Issue, Project, Team, WorkflowState } from "./types.linear"
import { ToolCard, ToolCardSkeleton } from "../common/tool-card"
import { Table, TableHeader, TableBody, TableCell, TableRow, TableHead } from "@/components/ui/table"
import { formatDistanceToNow } from "date-fns"

export function LinearIssueCard({ 
  id,
  title, 
  description, 
  state, 
  priority, 
  assignee, 
  creator, 
  createdAt, 
  labels,
  identifier,
  teamKey
}: Issue) {
  const priorityText = priority ? `P${priority}` : 'No priority'
  const formattedDate = (() => {
    try {
      const date = new Date(createdAt)
      if (isNaN(date.getTime())) {
        return 'Invalid date'
      }
      return formatDistanceToNow(date, { addSuffix: true })
    } catch {
      return 'Invalid date'
    }
  })()

  const subtitle = [
    state,
    priorityText,
    assignee ? `${assignee.name}` : 'Unassigned',
  ].join(' • ')

  return (
    <ToolCard
      resourceType="linear/issue"
      title={title}
      subtitle={subtitle}
      externalLink={`https://linear.app/${teamKey}/issue/${identifier}`}
    />
  )
}

export function LinearProjectList({ projects }: { projects: Project[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Project Name</TableHead>
          <TableHead>State</TableHead>
          <TableHead>Lead</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {projects.map((project) => (
          <TableRow key={project.id}>
            <TableCell>{project.name}</TableCell>
            <TableCell>{project.state.charAt(0).toUpperCase() + project.state.slice(1)}</TableCell>
            <TableCell>{project.lead?.name || 'No lead'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function LinearTeamList({ teams }: { teams: Team[] }) {
  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true })
    } catch (error) {
      return 'Invalid date'
    }
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Team Name</TableHead>
          <TableHead>Key</TableHead>
          <TableHead>Description</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {teams.map((team) => (
          <TableRow key={team.id}>
            <TableCell>{team.name}</TableCell>
            <TableCell>{team.key}</TableCell>
            <TableCell>{team.description || 'No description'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function LinearWorkflowStateList({ states }: { states: WorkflowState[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Team</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {states.map((state) => (
          <TableRow key={state.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: state.color }}
                />
                {state.name}
              </div>
            </TableCell>
            <TableCell>{state.type.charAt(0).toUpperCase() + state.type.slice(1)}</TableCell>
            <TableCell>{state.team_name || 'No team'}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function LinearWorkflowStateListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Team</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-20 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function LinearIssueCardSkeleton() {
  return <ToolCardSkeleton />
}

export function LinearProjectListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Project Name</TableHead>
          <TableHead>State</TableHead>
          <TableHead>Lead</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-20 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-24 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export function LinearTeamListSkeleton() {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Team Name</TableHead>
          <TableHead>Key</TableHead>
          <TableHead>Description</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {[1, 2, 3].map((i) => (
          <TableRow key={i}>
            <TableCell><div className="h-4 w-32 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-16 bg-gray-200 animate-pulse rounded" /></TableCell>
            <TableCell><div className="h-4 w-40 bg-gray-200 animate-pulse rounded" /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}