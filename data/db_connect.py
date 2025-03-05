import os

import certifi

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'

client = None

MONGO_ID = '_id'

# callahan_uri = f'mongodb+srv://gcallah:{password}'
# + '@koukoumongo1.yud9b.mongodb.net/'
# + '?retryWrites=true&w=majority'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print('Setting client because it is None.')

        # Debug environment variable
        cloud_mode = os.environ.get('CLOUD_MONGO', LOCAL)
        password = os.environ.get("MONGO_PASSWD")
        print(f"Debug: CLOUD_MONGO={cloud_mode}, MONGO_PASSWD={password}")

        if cloud_mode == CLOUD:
            if not password:
                raise ValueError('You must set MONGO_PASSWD to your password '
                                 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(f'mongodb+srv://at5604:{password}'
                                    + '@cluster0.6nvuo.mongodb.net/'
                                    + '?retryWrites=true'
                                    + '&w=majority'
                                    + '&appName=Cluster0'
                                    + '&connectTimeoutMS=10000'
                                    + '&socketTimeoutMS=10000'
                                    + '&connect=false'
                                    + '&maxPoolsize=1',
                                    tlsCAFile=certifi.where())
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()
    return client


def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    Returns the inserted document with its ID.
    """
    print(f'{db=}')
    result = client[db][collection].insert_one(doc)
    if result.inserted_id:
        doc['_id'] = result.inserted_id
        return doc
    return None


def fetch_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)

        return doc


def delete(collection: str, filt: dict, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


def update(collection, filters, update_dict, db=SE_DB):
    result = client[db][collection].update_one(filters, {'$set': update_dict})
    return result.modified_count > 0


def read(collection, db=SE_DB, no_id=True) -> list:
    """
    Return a list from the db.
    """
    ret = []
    for doc in client[db][collection].find():
        if no_id:
            if MONGO_ID in doc:
                del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    print(f"Raw records: {recs}")
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
    return ret


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        doc[MONGO_ID] = str(doc[MONGO_ID])


def read_one(collection, filt, db=SE_DB):
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc
