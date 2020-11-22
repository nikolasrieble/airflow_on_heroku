import datetime
import logging
import os

from airflow.contrib.hooks.ssh_hook import SSHHook
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from default import default_args
from htmldate import find_date
from mongo_utils import MongoDb
from newspaper import Article
from newspaper import ArticleException

logger = logging.getLogger("airflow.task")


def url_processor(language, **context):
    database = MongoDb()
    target = database.get_open_task(language)

    if target is None:
        logger.info('No task left')

    else:
        url = target["url"]
        logger.info('Extracting data from {}'.format(url))

        data = extract_data(url)

        logger.info('Upserting data')
        database.insert_article(data, language=language)


def extract_date(published_at, url):
    if not isinstance(published_at, datetime.datetime):
        published_at = find_date(url)
        if published_at:
            try:
                published_at = datetime.datetime.strptime(url, '%Y-%m-%d')
            except ValueError:
                published_at = None

    return published_at


def extract_data(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            'published_at': extract_date(article.publish_date, url),
            'text': article.text,
            'authors': list(article.authors),
            'title': article.title,
            'url': url,
            'tags': list(article.tags),
            'fetched_at': datetime.datetime.now()
        }
    except Exception:
        logger.info('No data could be extracted from {}'.format(url))
        return {
            'url': url,
            'text': "Could not be fetched",
            'fetched': False,
        }


LANGUAGES = ['de', 'tr']
START_DATES = [datetime.datetime(2020, 9, 1, 0, 0, 0), datetime.datetime(2020, 9, 1, 0, 0, 30)]
REMOTE_BIND_IP = os.environ['SERVER_REMOTE_BIND_IP']
REMOTE_BIND_PORT = os.environ['SERVER_REMOTE_BIND_PORT']
LOCAL_BIND_PORT = os.environ['SERVER_LOCAL_BIND_PORT']
USERNAME = os.environ['SERVER_USERNAME']
PASSWORD = os.environ['SERVER_PASSWORD']

ssh_hook = SSHHook(
    # ssh_conn_id='SERVER_ssh_connector',
    keepalive_interval=60,
    username=USERNAME,
    password=PASSWORD
).get_tunnel(
    int(REMOTE_BIND_PORT),
    remote_host=REMOTE_BIND_IP,
    local_port=int(LOCAL_BIND_PORT)
).start()


def create_dynamic_dag(dag_obj, language):
    with dag_obj:
        ssh_operator = SSHOperator(
            ssh_hook=ssh_hook,
            task_id='open_tunnel_to_SERVER',
            command='ls -al',
            dag=dag_obj
        )
        processor = PythonOperator(
            task_id='de_url_processor_operator',
            python_callable=url_processor,
            op_kwargs={'language': language}
        )
        processor.set_upstream(ssh_operator)

    return dag_obj


for language, start_date in zip(LANGUAGES, START_DATES):
    dag_id = f'{language}_url_processor'
    default_args["start_date"] = start_date
    dag = DAG(dag_id,
              schedule_interval='* * * * *',
              description='Scrape website for newspaper',
              default_args=default_args,
              catchup=False,
              )
    globals()[dag_id] = create_dynamic_dag(dag, language)
