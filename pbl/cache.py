import leveldb
import json
import os

cache_path = os.environ.get('PBL_CACHE_PATH')
if not cache_path:
    cache_path = '.cache'

db = leveldb.LevelDB(cache_path)

def put(type, tid, obj):
    key = get_key(type, tid)
    js = json.dumps(obj)
    db.Put(key, js)

def get(type, tid):
    key = get_key(type, tid)
    try:
        js = db.Get(key)
        return json.loads(js)
    except:
        return None

def get_key(type, id):
    return type + '-' + id
    
