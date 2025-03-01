'use client';

import React from 'react';

function DropboxFileCard(props: any) {
  const file = props.data;
  if (!file) return null;

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (date.toString() === 'Invalid Date') return '';
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatSize = (bytes: number | null | undefined) => {
    if (bytes === undefined || bytes === null) return 'Unknown size';
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (mimeType: string | null, isFolder: boolean) => {
    if (isFolder) return '📁';
    if (!mimeType) return '📄';
    if (mimeType.includes('image/')) return '🖼️';
    if (mimeType.includes('video/')) return '🎬';
    if (mimeType.includes('audio/')) return '🎵';
    if (mimeType.includes('text/')) return '📝';
    if (mimeType.includes('pdf')) return '📑';
    if (mimeType.includes('spreadsheet')) return '📊';
    if (mimeType.includes('presentation')) return '📽️';
    if (mimeType.includes('document')) return '📄';
    return '📄';
  };

  // Check if data is a FileList or DropboxFile
  const isFileList = file.files !== undefined;
  const fileData = isFileList ? file.files : [file];
  
  return (
    <div className="flex flex-wrap gap-4 justify-start w-full">
      {fileData.map((fileItem: any, index: number) => {
        const modifiedDate = formatDate(fileItem.modified_time);
        const fileIcon = getFileIcon(fileItem.mime_type, fileItem.is_folder);
        const fileSize = formatSize(fileItem.size);

        return (
          <div 
            key={fileItem.id} 
            className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm w-[300px] max-w-full font-sans mb-2 flex flex-col"
          >
            <div className="flex items-start mb-3">
              <div className="mr-3 flex items-center justify-center bg-blue-50 rounded-md p-2 text-blue-500">
                <span className="text-base">{fileIcon}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-base text-slate-800 mb-1 break-words">
                  {fileItem.name}
                </div>
                <div className="text-sm text-slate-500 mb-0.5">
                  {fileSize}
                </div>
                <div className="text-sm text-slate-500 mb-0.5">
                  Modified: {modifiedDate}
                </div>
              </div>
              {fileItem.shared_link && (
                <a
                  href={fileItem.shared_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-500 flex items-center justify-center ml-2 no-underline"
                >
                  <span className="text-base">🔗</span>
                </a>
              )}
            </div>
            
            {fileItem.path_display && (
              <div className="flex items-center mb-2 text-slate-500">
                <span className="mr-2 text-sm">📂</span>
                <span className="text-sm overflow-hidden text-ellipsis whitespace-nowrap">
                  Location: {fileItem.path_display}
                </span>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function JiraProjectCard(props: any) {
  const project = props.data;
  if (!project) return null;

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white shadow-sm w-[350px] max-w-full font-sans">
      <div className="flex items-start mb-4">
        <div className="mr-3 flex items-center justify-center bg-blue-50 rounded-md p-2 text-blue-500">
          <span className="text-base">📋</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-blue-600 mb-0.5">
            {project.key}
          </div>
          <div className="font-semibold text-lg text-slate-800 mb-1 break-words">
            {project.name}
          </div>
          {project.lead && (
            <div className="text-sm text-slate-500 mb-0.5">
              Lead: {project.lead}
            </div>
          )}
        </div>
        {project.url && (
          <a
            href={project.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-500 flex items-center justify-center ml-2 no-underline"
          >
            <span className="text-base">🔗</span>
          </a>
        )}
      </div>
      
      {project.description && (
        <div className="text-sm text-slate-600 mb-4 leading-relaxed">
          {project.description}
        </div>
      )}
      
      {project.components && project.components.length > 0 && (
        <>
          <div className="text-base font-semibold text-slate-800 mt-4 mb-2 border-b border-slate-200 pb-1">
            Components
          </div>
          <ul className="list-disc pl-5 mb-4">
            {project.components.map((component: any, index: number) => (
              <li key={index} className="text-sm text-slate-600 mb-1">
                {component.name}
              </li>
            ))}
          </ul>
        </>
      )}
      
      {project.versions && project.versions.length > 0 && (
        <>
          <div className="text-base font-semibold text-slate-800 mt-4 mb-2 border-b border-slate-200 pb-1">
            Versions
          </div>
          <div className="flex flex-wrap gap-2">
            {project.versions.map((version: any, index: number) => (
              <div key={index} className="bg-slate-100 px-2 py-1 rounded text-sm text-slate-700">
                {version.name} {version.released ? '(Released)' : '(Unreleased)'}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function JiraProjectsTable(props: any) {
  const projects = props.data;
  if (!projects || !projects.length) return null;

  // SVG Link Icon component
  const LinkIcon = () => (
    <svg width="10" height="10" viewBox="0 0 16 16" fill="none" style={{ color: '#64748b' }}>
      <path d="M6.5 9.5L9.5 6.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M4.5 7.5L3 9C2.17157 9.82843 2.17157 11.1716 3 12C3.82843 12.8284 5.17157 12.8284 6 12L7.5 10.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8.5 5.5L10 4C10.8284 3.17157 12.1716 3.17157 13 4C13.8284 4.82843 13.8284 6.17157 13 7L11.5 8.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );

  // Component for tag with initials
  const ComponentTag = ({ name }: { name: string }) => {
    const initials = name.substring(0, 2).toUpperCase();
    
    return (
      <div className="relative group">
        <div className="inline-flex items-center justify-center bg-[#ebf5ff] text-[#0052CC] text-xs px-2 py-0.5 rounded">
          {initials}
        </div>
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-1 hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
          {name}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-solid border-gray-800 border-b-transparent border-l-transparent border-r-transparent"></div>
        </div>
      </div>
    );
  };

  return (
    <div className="w-full overflow-x-auto">
      <div className="w-full bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="px-4 py-3 bg-slate-50 text-left flex border-b border-slate-200">
          <div className="w-[45%] text-sm font-semibold text-slate-700">Project</div>
          <div className="w-[40%] text-sm font-semibold text-slate-700">Components</div>
          <div className="w-[15%] text-sm font-semibold text-slate-700">Lead</div>
        </div>
        
        <div className="divide-y divide-slate-100">
          {projects.map((project: any, index: number) => (
            <div key={project.id} className="px-4 py-3 flex items-start hover:bg-slate-50 transition-colors">
              <div className="w-[45%]">
                <div className="flex items-center">
                  <span className="text-sm font-medium text-[#0052CC] mr-2">{project.key}</span>
                  <span className="text-sm font-medium text-slate-800 mr-2">{project.name}</span>
                  {project.url && (
                    <a
                      href={project.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#64748b] flex items-center justify-center"
                    >
                      <LinkIcon />
                    </a>
                  )}
                </div>
              </div>
              
              <div className="w-[40%]">
                <div className="flex flex-wrap gap-1">
                  {project.components && project.components.map((component: any) => (
                    <ComponentTag key={component.id} name={component.name} />
                  ))}
                </div>
              </div>
              
              <div className="w-[15%]">
                <span className="text-sm text-slate-700">{project.lead || '-'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ComponentTestingPage() {
  // Example data from the Dropbox component.json
  const dropboxExampleData = {
    files: [
      {
        id: "file:id:123456",
        name: "Project Proposal.docx",
        path_display: "/Documents/Project Proposal.docx",
        path_lower: "/documents/project proposal.docx",
        mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size: 2456789,
        is_folder: false,
        created_time: "2023-06-15T14:30:00Z",
        modified_time: "2023-06-16T09:45:00Z",
        shared_link: "https://www.dropbox.com/s/abc123/Project%20Proposal.docx"
      },
      {
        id: "folder:id:789012",
        name: "Images",
        path_display: "/Documents/Images",
        path_lower: "/documents/images",
        mime_type: null,
        size: null,
        is_folder: true,
        created_time: "2023-05-10T08:15:00Z",
        modified_time: "2023-06-14T16:30:00Z",
        shared_link: null
      },
      {
        id: "file:id:345678",
        name: "Quarterly Report.pdf",
        path_display: "/Documents/Quarterly Report.pdf",
        path_lower: "/documents/quarterly report.pdf",
        mime_type: "application/pdf",
        size: 5678901,
        is_folder: false,
        created_time: "2023-06-01T11:20:00Z",
        modified_time: "2023-06-02T14:15:00Z",
        shared_link: "https://www.dropbox.com/s/def456/Quarterly%20Report.pdf"
      }
    ],
    cursor: "AAHCpYYtXZ1L_AAAAAAAXR-hvsGHa2TPBZCiU-u0cjkYjYGFR7OXW_0WEgpfR9_nR1GgHjUOlJ1FKoFUNzKUMQ",
    has_more: false
  };

  // Example data for Jira Project Card
  const jiraProjectData = {
    id: "10000",
    key: "PROJ",
    name: "Sample Project",
    description: "This is a sample project for demonstration purposes.",
    lead: "John Doe",
    url: "https://yourcompany.atlassian.net/browse/PROJ",
    components: [
      {
        id: "10001",
        name: "Frontend"
      },
      {
        id: "10002",
        name: "Backend"
      },
      {
        id: "10003",
        name: "API"
      }
    ],
    versions: [
      {
        id: "10001",
        name: "v1.0.0",
        released: true,
        releaseDate: "2023-05-15"
      },
      {
        id: "10002",
        name: "v1.1.0",
        released: false
      },
      {
        id: "10003",
        name: "v2.0.0",
        released: false
      }
    ]
  };

  // Multiple projects data for the table
  const jiraProjectsData = [
    {
      id: "10000",
      key: "PROJ",
      name: "Sample Project",
      description: "This is a sample project for demonstration purposes.",
      lead: "John Doe",
      url: "https://yourcompany.atlassian.net/browse/PROJ",
      components: [
        { id: "10001", name: "Frontend" },
        { id: "10002", name: "Backend" },
        { id: "10003", name: "API" }
      ],
      versions: [
        { id: "10001", name: "v1.0.0", released: true, releaseDate: "2023-05-15" },
        { id: "10002", name: "v1.1.0", released: false },
        { id: "10003", name: "v2.0.0", released: false }
      ]
    },
    {
      id: "10001",
      key: "MOBILE",
      name: "Mobile Application",
      description: "Native mobile application for iOS and Android platforms.",
      lead: "Jane Smith",
      url: "https://yourcompany.atlassian.net/browse/MOBILE",
      components: [
        { id: "20001", name: "iOS" },
        { id: "20002", name: "Android" },
        { id: "20003", name: "Shared" }
      ],
      versions: [
        { id: "20001", name: "v2.5.0", released: true, releaseDate: "2023-04-10" },
        { id: "20002", name: "v2.6.0", released: true, releaseDate: "2023-06-01" },
        { id: "20003", name: "v3.0.0", released: false }
      ]
    },
    {
      id: "10002",
      key: "INFRA",
      name: "Infrastructure",
      description: "Cloud infrastructure and DevOps automation.",
      lead: "Mike Johnson",
      url: "https://yourcompany.atlassian.net/browse/INFRA",
      components: [
        { id: "30001", name: "AWS" },
        { id: "30002", name: "CI/CD" },
        { id: "30003", name: "Monitoring" }
      ],
      versions: [
        { id: "30001", name: "Q2-2023", released: true, releaseDate: "2023-06-30" },
        { id: "30002", name: "Q3-2023", released: false }
      ]
    }
  ];

  return (
    <div className="p-5 flex flex-col items-center justify-center min-h-screen bg-slate-50">
      <h1 className="mb-5 text-slate-800 text-2xl font-bold">Component Testing</h1>
      
      <div className="w-full max-w-6xl mb-10">
        <h2 className="mb-4 text-slate-700 text-xl font-semibold">Jira Projects Table</h2>
        <JiraProjectsTable data={jiraProjectsData} />
      </div>
      
      <div className="w-full max-w-4xl mb-10">
        <h2 className="mb-4 text-slate-700 text-xl font-semibold">Jira Project Card</h2>
        <JiraProjectCard data={jiraProjectData} />
      </div>
      
      <div className="w-full max-w-4xl">
        <h2 className="mb-4 text-slate-700 text-xl font-semibold">Dropbox File Card</h2>
        <DropboxFileCard data={dropboxExampleData} />
      </div>
    </div>
  );
}