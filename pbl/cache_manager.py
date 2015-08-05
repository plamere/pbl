import os
def get_cache():
    cache_type = os.environ.get('PBL_CACHE')
    if cache_type == 'REDIS':
        import redis_cache as cache
    elif cache_type == 'LEVELDB':
        import leveldb_cache as cache
    else: 
        import nocache as cache

    print 'cache', cache.name
    return cache
