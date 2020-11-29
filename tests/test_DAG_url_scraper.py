from unittest import TestCase
from dags.DAG_url_scraper import get_clean_urls
import mongomock as mongomock
from mongo_utils import MongoDb


class Test(TestCase):
    def test_get_clean_tasks(self):
        raw_urls = [
            'http://www.test.de/test_1',
            'https://www.test.de/test_1',
            'http://www.test.de/test_2#anchor',
        ]

        expected_cleaned_urls = [
            'https://www.test.de/test_1',
            'https://www.test.de/test_1',
        ]

        computed_cleaned_urls = get_clean_urls(raw_urls)

        assert computed_cleaned_urls == expected_cleaned_urls

    def test_only_one_article_inserted(self):
        origin_url = 'www.test.de'
        raw_urls = [
            'http://www.test.de/test_1',
            'https://www.test.de/test_1',
            'http://www.test.de/test_2',
            'http://www.test.de/test_2#anchor',
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        tasks = [{'url': cleaned_url, 'origin': origin_url} for cleaned_url in cleaned_urls]

        mongo_database = MongoDb()
        mongo_database._database = mongomock.MongoClient()["newspaper"]

        # when
        mongo_database.insert_tasks(tasks, "LANGUAGE")

        # then
        article_count = mongo_database._database["newspaper"]["LANGUAGE"].count_documents({})
        assert article_count == 2
