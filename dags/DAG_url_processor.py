import datetime

from airflow.models import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.python_operator import PythonOperator
from newspaper import Article
from newspaper import ArticleException

from default import default_args
from mongo_utils import MongoDb


def url_processor(**context):
    database = MongoDb()
    target = database.get_open_task()

    if target is not None:
        try:
            data = extract_data(target["url"])
            database.insert_article(data, language=target["language"])
            database.set_task_solved(target)
        except ArticleException:
            print('article could not be scraped from url {}'.format(article.url))


def extract_data(url):
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
