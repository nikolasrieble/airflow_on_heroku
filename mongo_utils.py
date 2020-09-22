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
        for task in tasks:
            collection.update_one(task, {"$set": task}, upsert=True)

    def get_open_task(self):
        collection = self._get_task_collection()
        return collection.find_one({'scraped': 0})

    def set_task_solved(self, task):
        collection = self._get_task_collection()
        return collection.update_one({'url': task['url']}, {'$set': {'scraped': 1}}, upsert=False)

    def get_target_urls(self, language):
        collection = self._get_target_collection()
        result = collection.find({'language': language})
        if result.count() == 0:
            return []
        return [i['url'] for i in result]

    def _get_task_collection(self):
        return self._database['TODO']

    def _get_target_collection(self):
        return self._database['TARGET']
