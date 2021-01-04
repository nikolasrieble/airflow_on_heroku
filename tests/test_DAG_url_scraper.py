from unittest import TestCase
from dags.DAG_url_scraper import get_clean_urls


class Test(TestCase):

    def test_get_clean_tasks(self):
        raw_urls = [
            'http://www.test.de/test_1',
            'https://www.test.de/test_1',
            'http://www.test.de/test_2',
            'http://test.de/test_2',
            'http://www.test.de/test_3#anchor',
            'http://www.test.de/test_4?something',
        ]

        expected_cleaned_urls = [
            'https://www.test.de/test_1',
            'https://www.test.de/test_2',
            'https://www.test.de/test_3',
            'https://www.test.de/test_4',
        ]

        computed_cleaned_urls = get_clean_urls(raw_urls)
        print(computed_cleaned_urls)

        assert len(computed_cleaned_urls) == len(expected_cleaned_urls)
        assert all([i in expected_cleaned_urls for i in computed_cleaned_urls])

    def test_http_and_https_articles_result_in_only_one_target(self):
        raw_urls = [
            'http://www.test.de/test_1',
            'https://www.test.de/test_1'
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_1']

    def test_with_www_and_without_www_articles_result_in_only_one_target(self):
        raw_urls = [
            'https://www.test.de/test_1',
            'https://test.de/test_1'
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_1']

    def test_anchors_are_removed_from_target(self):
        raw_urls = [
            'http://www.test.de/test_2',
            'http://www.test.de/test_2#anchor',
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_2']

    def test_question_mark_are_removed_from_target(self):
        raw_urls = [
            'http://www.test.de/test_2',
            'http://www.test.de/test_2?something',
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_2']

    def test_duplicate_is_ignored(self):
        raw_urls = [
            'http://www.test.de/test_2',
            'http://www.test.de/test_2'
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_2']

    def test_anchor_is_removed(self):
        raw_urls = [
            'http://www.test.de/test_2#ANCHOR'
        ]
        cleaned_urls = get_clean_urls(raw_urls)
        print(cleaned_urls)
        assert cleaned_urls == ['https://www.test.de/test_2']
