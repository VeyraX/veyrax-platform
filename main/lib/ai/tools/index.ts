import { createDraftTool, listMessagesTool, sendMessageTool } from './gmail';
import { listEventsTool, createEventTool } from './google-calendar';
import { listDatabasesTool, listPagesTool, createPageTool } from './notion';
import { getWeatherForecastTool } from './openweather';
import { askPerplexityTool } from './perplexity';

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
};

export type Tools = typeof tools;
