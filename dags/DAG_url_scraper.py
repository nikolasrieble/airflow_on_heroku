import newspaper
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from default import default_args
from mongo_utils import MongoDb
import logging


logger = logging.getLogger("airflow.task")


def create_task(article, language):
    return {'url': article.url,
            'scraped': 0,
            'language': language}


def url_scraper(language, **context):
    database = MongoDb()

    newspaper_url = database.get_target_urls(language)

    for url in newspaper_url:
        logger.info('Generating TODOs for {}'.format(url))
        paper = newspaper.build(url,
                            language=language,
                            memoize_articles=False,
                            fetch_images=False,
                            MIN_WORD_COUNT=100)

        logger.info('Creating tasks for {}'.format(url))
        tasks = [create_task(article, language) for article in paper.articles]

        logger.info('Inserting tasks for {}'.format(url))
        database.insert_tasks(tasks)


dag = DAG('url_scraper',
          schedule_interval='0 0 * * *',
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    tr_scraper = PythonOperator(task_id=f'url_scraper_tr', python_callable=url_scraper,
                                op_kwargs={'language': 'tr'})
    de_scraper = PythonOperator(task_id=f'url_scraper_de', python_callable=url_scraper,
                                op_kwargs={'language': 'de'})
    de_scraper.set_upstream(tr_scraper)
