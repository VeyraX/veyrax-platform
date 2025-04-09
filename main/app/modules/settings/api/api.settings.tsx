'use client';

import { createClient } from '@/lib/utils/supabase/client';
import { UserProfile, UserApiKey, UserSubscription } from './types.settings'
import * as CoreApi from './api.core.settings'

export async function getUserProfile(): Promise<UserProfile | null> {
  return CoreApi.getUserProfile(createClient())
}

export async function getUserApiKey(): Promise<UserApiKey | null> {
  return CoreApi.getUserApiKey(createClient())
}

export async function generateApiKey(): Promise<UserApiKey | null> {
  return CoreApi.generateApiKey(createClient(), () => {
    const randomBytes = new Uint8Array(20)
    window.crypto.getRandomValues(randomBytes)
    return randomBytes
  })
}

export async function revokeApiKey(): Promise<boolean> {
  return CoreApi.revokeApiKey(createClient())
}

export async function deleteUserAccount(): Promise<boolean> {
  return CoreApi.deleteUserAccount(createClient(), fetch)
}

export async function getUserSubscription() {
  return CoreApi.getUserSubscription(createClient())
}

export async function getUserUsage() {
  return CoreApi.getUserUsage(createClient())
}

export async function getUserProductInfo() {
  return CoreApi.getUserProductInfo(createClient())
}

export async function isUserOnFreePlan() {
  return CoreApi.isUserOnFreePlan(createClient())
}
export async function canUserCreateFlow(increment: number = 1) {
  return CoreApi.canUserCreateFlow(createClient(), increment)
}

export async function canUserCallAPI(increment: number = 1) {
  return CoreApi.canUserCallAPI(createClient(), increment)
}

export async function canUserSendMessage(increment: number = 1) {
  return CoreApi.canUserSendMessage(createClient(), increment)
}

export async function canUserRentKey() {
  return CoreApi.canUserRentKey(createClient())
}