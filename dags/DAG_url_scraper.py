import newspaper
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from default import default_args
from mongo_utils import MongoDb

input_list = {
    'tr': 'https://www.sozcu.com.tr/',
    'de': 'https://www.faz.net/',
}


def create_task(article, language):
    return {'url': article.url,
            'scraped': 0,
            'language': language}


def url_scraper(language, **context):
    database = MongoDb()

    newspaper_url = input_list.get(language)

    paper = newspaper.build(newspaper_url,
                            language=language,
                            memoize_articles=False,
                            fetch_images=False,
                            MIN_WORD_COUNT=100)

    tasks = [create_task(article, language) for article in paper.articles]
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
