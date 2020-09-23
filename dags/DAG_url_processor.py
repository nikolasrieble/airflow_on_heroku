import datetime
import logging

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from newspaper import Article
from newspaper import ArticleException

from default import default_args
from mongo_utils import MongoDb

logger = logging.getLogger("airflow.task")


def url_processor(**context):
    database = MongoDb()
    target = database.get_open_task()

    if target is None:
        logger.info('No task left')

    else:
        url = target["url"]
        logger.info('Extracting data from {}'.format(url))
        data = extract_data(url)

        if data is None:
            logger.info('No data could be extracted from {}'.format(url))
        else:
            logger.info('Upserting data for {}'.format(data["title"]))
            database.insert_article(data, language=target["language"])
        database.set_task_solved(target)


def extract_data(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            'published_at': article.publish_date,
            'text': article.text,
            'authors': list(article.authors),
            'title': article.title,
            'url': article.url,
            'tags': list(article.tags),
            'fetched_at': datetime.datetime.now()
        }
    except ArticleException:
        print('article could not be scraped from url {}'.format(url))
        return None


dag = DAG('url_processor',
          schedule_interval='* * * * *',
          description='Scrape website for newspaper',
          default_args=default_args,
          catchup=False,
          )

with dag:
    processor = PythonOperator(task_id='url_processor_operator',
                               python_callable=url_processor)
