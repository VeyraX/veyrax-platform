export const CACHE_KEYS = {
    AVAILABLE_MODELS: 'availableModels',
    USER_TOOLS: 'userTools',
    CONNECTED_TOOLS: 'connectedTools'
  };
  
  export const CACHE_DURATION = 15 * 60 * 1000;
  
  export type CacheOptions = {
    bypassCache?: boolean;
    forceRefresh?: boolean;
  }
  
  export class CacheUtils {
    static async getAvailableModels(
      fetcher: () => Promise<any>, 
      options: CacheOptions = {}
    ) {
      return this.getCachedData(
        CACHE_KEYS.AVAILABLE_MODELS, 
        fetcher, 
        options
      );
    }
  
    static async getUserTools(
      fetcher: () => Promise<any>, 
      options: CacheOptions = {}
    ) {
      return this.getCachedData(
        CACHE_KEYS.USER_TOOLS, 
        fetcher, 
        options
      );
    }
  
    static async getConnectedTools(
      fetcher: () => Promise<any>, 
      options: CacheOptions = {}
    ) {
      return this.getCachedData(
        CACHE_KEYS.CONNECTED_TOOLS, 
        fetcher, 
        options
      );
    }
  
    static invalidateCache(key: string) {
      localStorage.removeItem(key);
      localStorage.removeItem(`${key}_timestamp`);
    }
  
    static invalidateAllCaches() {
      Object.values(CACHE_KEYS).forEach(key => this.invalidateCache(key));
    }
  
    static updateCache(key: string, data: any) {
      this.invalidateCache(key);
      localStorage.setItem(key, JSON.stringify(data));
      localStorage.setItem(`${key}_timestamp`, Date.now().toString());
      
      return data;
    }
  
    private static async getCachedData(
      key: string, 
      fetcher: () => Promise<any>, 
      options: CacheOptions = {}
    ) {
      if (options.bypassCache) {
        return fetcher();
      }
  
      const cached = localStorage.getItem(key);
      const timestamp = localStorage.getItem(`${key}_timestamp`);
      
      if (cached && timestamp && !options.forceRefresh) {
        if (Date.now() - parseInt(timestamp) < CACHE_DURATION) {
          return JSON.parse(cached);
        }
      }
      
      const data = await fetcher();
      
      localStorage.setItem(key, JSON.stringify(data));
      localStorage.setItem(`${key}_timestamp`, Date.now().toString());
      
      return data;
    }
  } 