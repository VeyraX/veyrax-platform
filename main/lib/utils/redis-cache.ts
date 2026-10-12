import { Redis } from '@upstash/redis'

const redis = process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN
  ? new Redis({
      url: process.env.UPSTASH_REDIS_REST_URL,
      token: process.env.UPSTASH_REDIS_REST_TOKEN,
    })
  : null

const DEFAULT_TTL = 60 * 60 * 24 * 7

export const getCache = async <T>(key: string): Promise<T | null> => {
  if (!redis) return null
  try {
    return await redis.get(key)
  } catch (error) {
    console.error(`Redis cache get error for key ${key}:`, error)
    return null
  }
}

export const setCache = async <T>(key: string, value: T, ttl: number = DEFAULT_TTL): Promise<boolean> => {
  if (!redis) return false
  try {
    await redis.set(key, value, { ex: ttl })
    return true
  } catch (error) {
    console.error(`Redis cache set error for key ${key}:`, error)
    return false
  }
}

export const deleteCache = async (key: string): Promise<boolean> => {
  if (!redis) return false
  try {
    await redis.del(key)
    return true
  } catch (error) {
    console.error(`Redis cache delete error for key ${key}:`, error)
    return false
  }
}

export const deleteCacheByPattern = async (pattern: string): Promise<boolean> => {
  if (!redis) return false
  try {
    const keys = await redis.keys(pattern)
    if (keys.length > 0) {
      await redis.del(...keys)
    }
    return true
  } catch (error) {
    console.error(`Redis cache delete by pattern error for pattern ${pattern}:`, error)
    return false
  }
}

export const getRedisClient = () => redis

export default {
  getCache,
  setCache,
  deleteCache,
  deleteCacheByPattern,
  getRedisClient
} 