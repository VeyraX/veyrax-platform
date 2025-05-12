const DB_NAME = 'veyraxCache';
const DB_VERSION = 1;
const DEFAULT_TTL =  24 * 60 * 60 * 1000;

export enum CacheStore {
  INTEGRATIONS = 'integrationsCache',
  MCP = 'mcpCache',
  AGENTS = 'agentsCache',
  FLOWS = 'flowsCache',
  USER_DATA = 'userDataCache'
}

interface CacheItem<T> {
  data: T;
  userId: string;
  expiresAt: number;
  cacheKey: string;
}

const storeConfigs = {
  [CacheStore.INTEGRATIONS]: { keyPath: 'cacheKey', indexes: ['userId', 'expiresAt'] },
  [CacheStore.MCP]: { keyPath: 'cacheKey', indexes: ['userId', 'expiresAt'] },
  [CacheStore.AGENTS]: { keyPath: 'cacheKey', indexes: ['userId', 'expiresAt'] },
  [CacheStore.FLOWS]: { keyPath: 'cacheKey', indexes: ['userId', 'expiresAt'] },
  [CacheStore.USER_DATA]: { keyPath: 'cacheKey', indexes: ['userId', 'expiresAt'] }
};

const initDB = (): Promise<IDBDatabase> => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      
      Object.entries(storeConfigs).forEach(([storeName, config]) => {
        if (!db.objectStoreNames.contains(storeName)) {
          const store = db.createObjectStore(storeName, { keyPath: config.keyPath });
          config.indexes.forEach(indexName => {
            store.createIndex(indexName, indexName, { unique: false });
          });
        }
      });
    };
    
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
};

export const setCacheItem = async <T>(
  store: CacheStore,
  key: string, 
  userId: string, 
  data: T, 
  ttl = DEFAULT_TTL
): Promise<void> => {
  try {
    const db = await initDB();
    const tx = db.transaction(store, 'readwrite');
    const objectStore = tx.objectStore(store);
    
    const cacheKey = `${userId}:${key}`;
    const expiresAt = Date.now() + ttl;
    
    objectStore.put({
      cacheKey,
      userId,
      data,
      expiresAt
    });
    
    return new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch (error) {
    console.error(`Error setting cache item in ${store}:`, error);
  }
};

export const getCacheItem = async <T>(
  store: CacheStore,
  key: string, 
  userId: string
): Promise<T | null> => {
  try {
    const db = await initDB();
    const tx = db.transaction(store, 'readonly');
    const objectStore = tx.objectStore(store);
    
    const cacheKey = `${userId}:${key}`;
    const request = objectStore.get(cacheKey);
    
    return new Promise((resolve, reject) => {
      request.onsuccess = () => {
        const cacheItem = request.result as CacheItem<T> | undefined;
        
        if (!cacheItem) {
          resolve(null);
          return;
        }
        
        if (cacheItem.expiresAt < Date.now()) {
          const deleteTx = db.transaction(store, 'readwrite');
          const deleteStore = deleteTx.objectStore(store);
          deleteStore.delete(cacheKey);
          resolve(null);
          return;
        }
        
        resolve(cacheItem.data);
      };
      request.onerror = () => reject(request.error);
    });
  } catch (error) {
    console.error(`Error getting cache item from ${store}:`, error);
    return null;
  }
};

export const deleteCacheItem = async (
  store: CacheStore,
  key: string, 
  userId: string
): Promise<void> => {
  try {
    const db = await initDB();
    const tx = db.transaction(store, 'readwrite');
    const objectStore = tx.objectStore(store);
    
    const cacheKey = `${userId}:${key}`;
    objectStore.delete(cacheKey);
    
    return new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch (error) {
    console.error(`Error deleting cache item from ${store}:`, error);
  }
};

export const clearUserStoreCache = async (
  store: CacheStore,
  userId: string
): Promise<void> => {
  try {
    const db = await initDB();
    const tx = db.transaction(store, 'readwrite');
    const objectStore = tx.objectStore(store);
    const index = objectStore.index('userId');
    const request = index.openCursor(IDBKeyRange.only(userId));
    
    request.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest).result;
      if (cursor) {
        cursor.delete();
        cursor.continue();
      }
    };
    
    return new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch (error) {
    console.error(`Error clearing user cache from ${store}:`, error);
  }
};

export const clearAllUserCache = async (userId: string): Promise<void> => {
  try {
    const storeNames = Object.values(CacheStore);
    for (const store of storeNames) {
      await clearUserStoreCache(store, userId);
    }
  } catch (error) {
    console.error('Error clearing all user cache:', error);
  }
};

export const cleanExpiredStoreCache = async (store: CacheStore): Promise<void> => {
  try {
    const db = await initDB();
    const tx = db.transaction(store, 'readwrite');
    const objectStore = tx.objectStore(store);
    const index = objectStore.index('expiresAt');
    const now = Date.now();
    const request = index.openCursor(IDBKeyRange.upperBound(now));
    
    request.onsuccess = (event) => {
      const cursor = (event.target as IDBRequest).result;
      if (cursor) {
        cursor.delete();
        cursor.continue();
      }
    };
    
    return new Promise((resolve, reject) => {
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  } catch (error) {
    console.error(`Error cleaning expired cache from ${store}:`, error);
  }
};

export const cleanAllExpiredCache = async (): Promise<void> => {
  try {
    const storeNames = Object.values(CacheStore);
    for (const store of storeNames) {
      await cleanExpiredStoreCache(store);
    }
  } catch (error) {
    console.error('Error cleaning all expired cache:', error);
  }
};