import logging

import newspaper
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from default import default_args
from mongo_utils import MongoDb

logger = logging.getLogger("airflow.task")


def get_clean_urls(raw_urls):
    """
    Known problems so far:
    https vs http
    https://www.test.de vs https://test.de
    https://www.test.de/something vs https://www.test.de/something#something
    https://www.test.de/something.html vs https://www.test.de/something.html?something
    """
    cleaned_urls = []
    for url in raw_urls:
        # Removing same html links with anchors (#) or question mark (?)
        url = url.split('#')[0].split('?')[0]

        # http vs https
        url = url.replace('http:', 'https:')

        # www
        if 'www' not in url[:12]:
            url = url.replace('https://', 'https://www.')

        cleaned_urls.append(url)

    return list(set(cleaned_urls))


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

        raw_urls = [article.url for article in paper.articles]
        cleaned_urls = get_clean_urls(raw_urls)
        tasks = [{'url': cleaned_url, 'origin': url} for cleaned_url in cleaned_urls]

        logger.info('Inserting tasks for {}'.format(url))
        database.insert_tasks(tasks, language)


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
