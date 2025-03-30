import { tool_call, run_flow } from "./tool-call";

export const tools = {
  tool_call,
  run_flow
};

export type Tools = typeof tools;
