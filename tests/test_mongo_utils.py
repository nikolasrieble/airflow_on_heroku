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

    def test_insert_into_empty_db(self):
        # given
        db = MongoDb()
        db.myclient = mongomock.MongoClient()
        expected_article = {"title": "How Millennials Are Disrupting Test"}

        # when
        db.insert(expected_article, "LANGUAGE")

        # then
        actual_article = db.myclient["newspaper"]["LANGUAGE"].find_one({})
        assert actual_article["title"] == expected_article["title"]

    def test_insert_does_not_create_duplicate(self):
        # given
        db = MongoDb()
        db.myclient = mongomock.MongoClient()
        existing_article = {"title": "How Millennials Are Disrupting Test"}
        existing_article["_id"] = db.myclient["newspaper"]["LANGUAGE"].insert_one(existing_article).inserted_id

        # when
        db.insert(existing_article, "LANGUAGE")

        # then
        article_count = db.myclient["newspaper"]["LANGUAGE"].count_documents({})
        assert article_count == 1

