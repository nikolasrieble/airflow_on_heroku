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
