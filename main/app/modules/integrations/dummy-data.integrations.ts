import { IntegrationCardProps } from './api/types.integrations';

export const dummyApiCards: IntegrationCardProps[] = [
  {
    id: '1',
    name: 'Gmail',
    description: 'Send and manage emails, organize inbox, and automate email workflows. Agents can handle email communications and scheduling.',
    logo: '/logos/gmail-logo.svg',
    provider_tag: 'gmail',
    categories: ['Communication'],
    connected: true
  },
  {
    id: '2',
    name: 'Google Drive',
    description: 'Manage files and documents in the cloud, handle sharing permissions, and collaborate on content. Agents can organize and manage document workflows.',
    logo: '/logos/drive-logo.svg',
    provider_tag: 'google-drive',
    categories: ['Storage'],
    connected: false
  },
  {
    id: '11',
    name: 'Google Calendar',
    description: 'Schedule meetings, manage events, and coordinate calendars across teams. Agents can handle appointment scheduling and time management.',
    logo: '/logos/google-calendar-logo.svg',
    provider_tag: 'google-calendar',
    categories: ['Business'],
    connected: true
  },
  {
    id: '3',
    name: 'Linear',
    description: 'Track software projects, manage issues, and coordinate development workflows. Agents can help manage development tasks and timelines.',
    logo: '/logos/linear-logo.svg',
    provider_tag: 'linear',
    categories: ['Development'],
    connected: true
  },
  {
    id: '4',
    name: 'Jira',
    description: 'Plan, track, and manage agile software development projects. Agents can help with issue tracking and sprint planning.',
    logo: '/logos/jira-logo.svg',
    provider_tag: 'jira',
    categories: ['Development', 'Business'],
    connected: false
  },
  {
    id: '5',
    name: 'Confluence',
    description: 'Create, organize, and collaborate on team documentation and knowledge bases. Agents can maintain and update documentation.',
    logo: '/logos/confluence-logo.svg',
    provider_tag: 'confluence',
    categories: ['Collaboration', 'Business'],
    connected: false
  },
  {
    id: '6',
    name: 'Perplexity',
    description: 'Access AI-powered research and information discovery. Agents can perform detailed research and provide accurate information.',
    logo: '/logos/perplexity-logo.svg',
    provider_tag: 'perplexity',
    categories: ['Research', 'AI'],
    connected: true
  },
  {
    id: '7',
    name: 'Slack',
    description: 'Coordinate team communications and automate notifications. Agents can manage channels and facilitate team collaboration.',
    logo: '/logos/slack-logo.svg',
    provider_tag: 'slack',
    categories: ['Communication'],
    connected: false
  },
  {
    id: '8',
    name: 'Notion',
    description: 'Create and organize documents, manage knowledge bases, and collaborate on content. Agents can help maintain documentation and workflows.',
    logo: '/logos/notion-logo.svg',
    provider_tag: 'notion',
    categories: ['Collaboration'],
    connected: true
  },
  {
    id: '9',
    name: 'Outlook',
    description: 'Manage emails, calendar, and contacts in Microsoft ecosystem. Agents can handle email organization and meeting scheduling.',
    logo: '/logos/outlook-logo.svg',
    provider_tag: 'outlook',
    categories: ['Communication'],
    connected: false
  },
  {
    id: '10',
    name: 'OpenWeather',
    description: 'Access real-time weather data and forecasts worldwide. Agents can provide weather updates and planning recommendations.',
    logo: '/logos/openweather-logo.png',
    provider_tag: 'openweather',
    categories: ['Weather'],
    connected: false
  }
];