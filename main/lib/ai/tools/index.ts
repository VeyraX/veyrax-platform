import { gmail_createDraft, gmail_listMessages, gmail_sendMessage } from './gmail';
import { googleCalendar_listEvents, googleCalendar_createEvent } from './google-calendar';
import { notion_listDatabases, notion_listPages, notion_createPage, notion_readPage, notion_vectorSearch, notion_searchPages, notion_getDatabaseProperties, notion_queryDatabase, notion_updatePage } from './notion';
import { openweather_getWeather } from './openweather';
import { perplexity_ask } from './perplexity';
import { googleDrive_listFiles, googleDrive_listFolders, googleDrive_getFile, googleDrive_moveFile, googleDrive_readFile, googleDrive_vectorSearch } from './google-drive';
import { linear_listIssues, linear_searchIssues, linear_createIssue, linear_listProjects, linear_listTeams, linear_updateIssue, linear_listWorkflowStates } from './linear';
import { 
  confluence_listSpaces,
  confluence_listPages,
  confluence_getPage,
  confluence_searchContent,
  confluence_vectorSearch 
} from './confluence';
import {
  jira_listIssues,
  jira_getIssue,
  jira_createIssue,
  jira_listProjects,
  jira_updateIssue,
  jira_deleteIssue,
  jira_getProject,
  jira_listStatuses,
  jira_listPriorities,
  jira_listIssueTypes,
  jira_listFields,
  jira_listUsers
} from './jira';
import { outlook_listMessages, outlook_sendMessage, outlook_createDraft, outlook_listEvents, outlook_createEvent, outlook_updateEvent } from './outlook';

export const tools = {
  gmail_createDraft,
  gmail_listMessages,
  gmail_sendMessage,
  googleCalendar_listEvents,
  googleCalendar_createEvent,
  notion_listDatabases,
  notion_listPages,
  notion_createPage,
  openweather_getWeather,
  perplexity_ask,
  googleDrive_listFiles,
  googleDrive_listFolders,
  googleDrive_getFile,
  googleDrive_moveFile,
  googleDrive_readFile,
  notion_readPage,
  notion_vectorSearch,
  notion_searchPages,
  googleDrive_vectorSearch,
  linear_listIssues,
  linear_searchIssues,
  linear_createIssue,
  linear_listProjects,
  linear_listTeams,
  linear_updateIssue,
  linear_listWorkflowStates,
  notion_getDatabaseProperties,
  notion_queryDatabase,
  notion_updatePage,
  confluence_listSpaces,
  confluence_listPages,
  confluence_getPage,
  confluence_searchContent,
  confluence_vectorSearch,
  jira_listIssues,
  jira_getIssue,
  jira_createIssue,
  jira_listProjects,
  jira_updateIssue,
  jira_deleteIssue,
  jira_getProject,
  jira_listStatuses,
  jira_listPriorities,
  jira_listIssueTypes,
  jira_listFields,
  jira_listUsers,
  outlook_listMessages,
  outlook_sendMessage,
  outlook_createDraft,
  outlook_listEvents,
  outlook_createEvent,
  outlook_updateEvent,
};

export type Tools = typeof tools;
