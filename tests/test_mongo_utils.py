from unittest import TestCase

import mongomock as mongomock

from mongo_utils import MongoDb


class Test(TestCase):

    def test_MongoDB_get_open_task_returns_none_for_empty_collection(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]

        # when
        task = mongo_database.get_open_task()

        # then
        assert task is None

    def test_MongoDB_get_open_task_returns_none_if_no_task_open(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        mongo_database._database["TODO"].insert_one({"scraped": 1, "id": 1})

        # when
        task = mongo_database.get_open_task()

        # then
        assert task is None

    def test_MongoDB_get_open_task_returns_open_task(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        open_task = {"scraped": 0, "id": 1}
        open_task['_id'] = mongo_database._database["TODO"].insert_one(open_task).inserted_id

        # when
        task = mongo_database.get_open_task()

        # then
        assert task == open_task

    def test_insert_into_empty_db(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        expected_article = {"title": "How Millennials Are Disrupting Test"}

        # when
        mongo_database.insert_article(expected_article, "LANGUAGE")

        # then
        actual_article = mongo_database._database["LANGUAGE"].find_one({})
        assert actual_article["title"] == expected_article["title"]

    def test_insert_does_not_create_duplicate(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        existing_article = {"title": "How Millennials Are Disrupting Test"}
        existing_article["_id"] = mongo_database._database["newspaper"]["LANGUAGE"].insert_one(
            existing_article).inserted_id

        # when
        mongo_database.insert_article(existing_article, "LANGUAGE")

        # then
        article_count = mongo_database._database["newspaper"]["LANGUAGE"].count_documents({})
        assert article_count == 1

    def test_set_task_solved(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        open_task = {"scraped": 0, "url": "www.google.com"}
        open_task['_id'] = mongo_database._database["TODO"].insert_one(open_task).inserted_id

        # when
        mongo_database.set_task_solved(open_task)

        # then
        actual_task = mongo_database._database["TODO"].find_one({"url": "www.google.com"})
        assert actual_task["url"] == open_task["url"]
        assert actual_task["scraped"] == 1
