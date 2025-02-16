import { createDraftTool, listMessagesTool, sendMessageTool } from './gmail';
import { listEventsTool, createEventTool } from './google-calendar';
import { listDatabasesTool, listPagesTool, createPageTool, readNotionPageTool } from './notion';
import { getWeatherForecastTool } from './openweather';
import { askPerplexityTool } from './perplexity';
import { listFilesTool, listFoldersTool, getFileTool, moveFileTool, readFileTool } from './google-drive';

export const tools = {
  createDraftTool,
  listMessagesTool,
  sendMessageTool,
  listEventsTool,
  createEventTool,
  listDatabasesTool,
  listPagesTool,
  createPageTool,
  getWeatherForecastTool,
  askPerplexityTool,
  listFilesTool,
  listFoldersTool,
  getFileTool,
  moveFileTool,
  readFileTool,
  readNotionPageTool
};

export type Tools = typeof tools;
