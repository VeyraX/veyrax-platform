import { tool_call, get_flow } from "./tool-call";

export const tools = {
  tool_call,
  get_flow
};

export type Tools = typeof tools;
