import os
import pymongo

CONNECTION_STRING = 'MONGO_DB'
DB_NAME = 'newspaper'
TARGET_COLLECTION = 'TARGET'


class MongoDb:

    def __init__(self):
        mongodb_string = os.environ.get(CONNECTION_STRING)
        self._database = pymongo.MongoClient(mongodb_string)[DB_NAME]

    def insert_article(self, data: dict, language):
        collection = self._database[language]
        collection.update_one({"url": data["url"]}, {"$set": data}, upsert=True)

    def insert_tasks(self, tasks, language):
        collection = self._database[language]
        for task in tasks:
            collection.update_one({"url": task["url"]}, {"$set": task}, upsert=True)

    def get_open_task(self, language):
        collection = self._database[language]
        return collection.find_one({"text": {"$exists": False}})

    def get_target_urls(self, language):
        collection = self._database[TARGET_COLLECTION]
        result = collection.find({'language': language})
        if result.count() == 0:
            return []
        return [i['url'] for i in result]
