import logging

import newspaper
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator

from default import default_args
from mongo_utils import MongoDb

logger = logging.getLogger("airflow.task")
REMOTE_BIND_IP = os.environ['SERVER_REMOTE_BIND_IP']
REMOTE_BIND_PORT = os.environ['SERVER_REMOTE_BIND_PORT']
LOCAL_BIND_PORT = os.environ['SERVER_LOCAL_BIND_PORT']
USERNAME = os.environ['SERVER_USERNAME']
PASSWORD = os.environ['SERVER_PASSWORD']

ssh_hook = SSHHook(
    ssh_conn_id='SERVER_ssh_connector',
    keepalive_interval=60,
    username=USERNAME,
    password=PASSWORD
).get_tunnel(
    int(REMOTE_BIND_PORT),
    remote_host=REMOTE_BIND_IP,
    local_port=int(LOCAL_BIND_PORT)
).start()


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
        tasks = [{'url': article.url, 'origin': url} for article in paper.articles]

        logger.info('Inserting tasks for {}'.format(url))
        database.insert_tasks(tasks, language)


dag = DAG('url_scraper',
          schedule_interval='0 0 * * *',
          description=f'''Scrape website for newspaper''',
          default_args=default_args,
          catchup=False,
          )

with dag:
    ssh_operator = SSHOperator(
        ssh_hook=ssh_hook,
        task_id='open_tunnel_to_SERVER',
        command='ls -al',
        dag=dag_obj
    )
    tr_scraper = PythonOperator(task_id=f'url_scraper_tr', python_callable=url_scraper,
                                op_kwargs={'language': 'tr'})
    de_scraper = PythonOperator(task_id=f'url_scraper_de', python_callable=url_scraper,
                                op_kwargs={'language': 'de'})
    de_scraper.set_upstream(tr_scraper)
    tr_scraper.set_upstream(ssh_operator)
