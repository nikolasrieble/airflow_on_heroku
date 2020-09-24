from unittest import TestCase

import mongomock as mongomock

from mongo_utils import MongoDb


class Test(TestCase):

    def test_MongoDB_get_open_task_returns_none_for_empty_collection(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]

        # when
        task = mongo_database.get_open_task('tr')

        # then
        assert task is None

    def test_MongoDB_get_open_task_returns_none_if_no_task_open(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        mongo_database._database["tr"].insert_one({"text": "This article is scraped"})

        # when
        task = mongo_database.get_open_task("tr")

        # then
        assert task is None

    def test_MongoDB_get_open_task_returns_open_task(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        open_task = {"url": "www.opentask.com"}
        open_task['_id'] = mongo_database._database["de"].insert_one(open_task).inserted_id

        # when
        task = mongo_database.get_open_task("de")

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

    def test_get_target_url(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        target_1 = {'language': 'de', 'url': 'www.news1.de'}
        mongo_database._database["TARGET"].insert_one(target_1)
        target_2 = {'language': 'de', 'url': 'www.news2.de'}
        mongo_database._database["TARGET"].insert_one(target_2)

        # when
        targets = mongo_database.get_target_urls('de')

        # then

        assert len(targets) == 2
        assert 'www.news2.de' in targets
        assert 'www.news1.de' in targets

    def test_get_target_url_does_not_throw_if_empty_if_collection_does_not_exist(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]
        # when
        mongo_database.get_target_urls('de')

    def test_insert_tasks_does_not_reinsert_solved_task(self):
        # given
        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]

        mongo_database._database["tr"].insert_one({'url': 'www.bike.com',
                                                   'text': "this article is scraped"})
        # when
        mongo_database.insert_tasks([{'url': 'www.bike.com'}],
                                    "tr")

        # then
        total = [i for i in mongo_database._database["tr"].find({'url': 'www.bike.com'})]

        assert total[0]["text"] == "this article is scraped"
        assert len(total) == 1
