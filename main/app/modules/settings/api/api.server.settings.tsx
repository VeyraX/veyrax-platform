import { createClient } from '@/lib/utils/supabase/server';
import * as CoreApi from './api.core.settings';
import { fetch } from 'next/dist/compiled/@edge-runtime/primitives';


// Серверные функции - обертки над ядром
export async function getUserSubscriptionServer() {
  return CoreApi.getUserSubscription(createClient());
}

export async function getUserUsageServer() {
  return CoreApi.getUserUsage(createClient());
}

export async function getProductInfoByTagServer(tag: string) {
  return CoreApi.getProductInfoByTag(createClient(), tag);
}

export async function getUserProductInfoServer() {
  return CoreApi.getUserProductInfo(createClient());
}

export async function isUserOnFreePlanServer() {
  return CoreApi.isUserOnFreePlan(createClient());
}

export async function getUserPlanNameServer() {
  return CoreApi.getUserPlanName(createClient());
}

export async function canUserCreateFlowServer(increment: number = 1) {
  return CoreApi.canUserCreateFlow(createClient(), increment);
}

export async function canUserSendMessageServer(increment: number = 1) {
  return CoreApi.canUserSendMessage(createClient(), increment);
}

export async function canUserCallAPIServer(increment: number = 1) {
  return CoreApi.canUserCallAPI(createClient(), increment);
}

export async function getUserApiKeyServer() {
  return CoreApi.getUserApiKey(createClient());
}

export async function revokeApiKeyServer() {
  return CoreApi.revokeApiKey(createClient());
}

export async function deleteUserAccountServer() {
  return CoreApi.deleteUserAccount(createClient(), fetch);
}
