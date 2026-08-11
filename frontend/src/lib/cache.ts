// Zero-dependency Promise deduplication and LRU caching
// Prevents race conditions during rapid state transitions

type CacheEntry<T> = {
  promise: Promise<T>;
  timestamp: number;
};

const promiseCache = new Map<string, CacheEntry<any>>();
const CACHE_TTL_MS = 5000; // 5 seconds for deduplication window

export async function cachedFetch<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl: number = CACHE_TTL_MS
): Promise<T> {
  const now = Date.now();
  const cached = promiseCache.get(key);

  if (cached && (now - cached.timestamp < ttl)) {
    return cached.promise;
  }

  // Create a new promise and store it before it resolves (deduplication)
  const promise = fetchFn().catch(err => {
    promiseCache.delete(key);
    throw err;
  });

  promiseCache.set(key, {
    promise,
    timestamp: now
  });

  return promise;
}

export function invalidateCache(prefix: string) {
  for (const key of promiseCache.keys()) {
    if (key.startsWith(prefix)) {
      promiseCache.delete(key);
    }
  }
}
