import { gmail_createDraft, gmail_listMessages, gmail_sendMessage } from './gmail';
import { googleCalendar_listEvents, googleCalendar_createEvent } from './google-calendar';
import { notion_listDatabases, notion_listPages, notion_createPage, notion_readPage, notion_vectorSearch, notion_searchPages } from './notion';
import { openweather_getWeather } from './openweather';
import { perplexity_ask } from './perplexity';
import { googleDrive_listFiles, googleDrive_listFolders, googleDrive_getFile, googleDrive_moveFile, googleDrive_readFile, googleDrive_vectorSearch } from './google-drive';
import { linear_listIssues, linear_searchIssues, linear_createIssue, linear_listProjects, linear_listTeams, linear_updateIssue, linear_listWorkflowStates } from './linear';


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
  linear_listWorkflowStates
};

export type Tools = typeof tools;
