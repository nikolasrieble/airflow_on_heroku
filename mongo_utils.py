import os
import pymongo


class MongoDb:

    def __init__(self):
        mongodb_string = os.environ.get('MONGO_DB')
        self._database = pymongo.MongoClient(mongodb_string)['newspaper']

    def insert_article(self, data: dict, language):
        collection = self._database[language]
        collection.update_one(data, {"$set": data}, upsert=True)

    def insert_tasks(self, tasks):
        collection = self._get_task_collection()
        return collection.insert_many(tasks)

    def get_open_task(self):
        collection = self._get_task_collection()
        return collection.find_one({'scraped': 0})

    def set_task_solved(self, task):
        collection = self._get_task_collection()
        return collection.update_one({'url': task['url']}, {'$set': {'scraped': 1}}, upsert=False)

    def _get_task_collection(self):
        return self._database['TODO']
