import datetime

from airflow.models import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python_operator import PythonOperator
from newspaper import Article
from newspaper import ArticleException

from mongo_utils import MongoDb

default_args = {
    'owner': 'niko_huy',
    'start_date': datetime.datetime(2020, 2, 18),
    'provide_context': True,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'execution_timeout': datetime.timedelta(minutes=60),
    'pool': 'default_pool'
}


def url_processor(**context):
    database = MongoDb()
    target = database.get_open_task()

    if target is not None:

        article = Article(target["url"])

        try:
            article.download()
            article.parse()

            data = extract_data(article)

            database.insert(data, language=target["language"])
            database.set_task_solved(target)

        except ArticleException:
            print('article could not be scraped from url {}'.format(article.url))


def extract_data(article):
    return {
        'published_at': article.publish_date,
        'text': article.text,
        'authors': list(article.authors),
        'title': article.title,
        'url': article.url,
        'tags': list(article.tags),
        'fetched_at':datetime.datetime.now()
    }


def conditionally_trigger(context, dag_run_obj):
    database = MongoDb()
    target = database.get_open_task()
    if target is not None:
        return dag_run_obj


dag = DAG('url_processor',
          schedule_interval='0 0 * * *',
          description='Scrape website for newspaper',
          default_args=default_args,
          catchup=False,
          )

with dag:
    processor = PythonOperator(task_id='url_processor_operator',
                               python_callable=url_processor)
    trigger = TriggerDagRunOperator(
        task_id='trigger_url_processor_operator',
        trigger_dag_id="url_processor",
        python_callable=conditionally_trigger
    )
    trigger.set_upstream(processor)
