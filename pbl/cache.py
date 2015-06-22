import leveldb
import json


db = leveldb.LevelDB('.cache')


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
    
