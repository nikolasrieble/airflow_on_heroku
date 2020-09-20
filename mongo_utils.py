import os
import pymongo


class MongoDb:

    def __init__(self):
        mongodb_string = os.environ.get('MONGO_DB')
        self.myclient = pymongo.MongoClient(mongodb_string)

    def insert(self, data: dict, language):
        mydb = self.myclient['newspaper']
        collection = mydb[language]
        # prevent duplicates
        # TODO include other fields in duplicate check - duplicate title only should be allowed
        if collection.count_documents({'title': data["title"]}) == 0:
            collection.insert_one(data)

    def get_open_task(self):
        database = self.myclient['TODO']
        collection = database['TODO']
        return collection.find_one({'scraped': 0})

    def set_task_solved(self, task):
        database = self.myclient['TODO']
        collection = database['TODO']
        return collection.update_one({'url': task['url']}, {'$set': {'scraped': 1}}, upsert=False)
