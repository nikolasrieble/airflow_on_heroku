from unittest import TestCase

import mongomock as mongomock

from mongo_utils import MongoDb


class Test(TestCase):

    def test_MongoDB_get_open_task_returns_none_for_empty_collection(self):
        # given
        db = MongoDb()
        db.myclient = mongomock.MongoClient()
        # when
        task = db.get_open_task()
        # then
        assert task == None

    def test_MongoDB_get_open_task_returns_none_if_no_task_open(self):
        # given
        db = MongoDb()
        db.myclient = mongomock.MongoClient()
        db.myclient["TODO"]["TODO"].insert_one({"scraped": 1, "id": 1})
        # when
        task = db.get_open_task()
        # then
        assert task == None

    def test_MongoDB_get_open_task_returns_open_task(self):
        # given
        db = MongoDb()
        db.myclient = mongomock.MongoClient()

        open_task = {"scraped": 0, "id": 1}
        open_task['_id'] = db.myclient["TODO"]["TODO"].insert_one(open_task).inserted_id
        # when
        task = db.get_open_task()
        # then
        assert task == open_task

    def test_MockMongo(self):

        def increase_votes(collection):
            collection.update_many({}, {'$inc': {'votes': 1}})

        collection = mongomock.MongoClient().db.collection
        objects = [dict(votes=1), dict(votes=2)]
        for obj in objects:
            obj['_id'] = collection.insert_one(obj).inserted_id
        increase_votes(collection)
        for obj in objects:
            stored_obj = collection.find_one({'_id': obj['_id']})
            stored_obj['votes'] -= 1
            assert stored_obj == obj  # by comparing all fields we make sure only votes changed
