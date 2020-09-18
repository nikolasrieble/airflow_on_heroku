# airflow_on_heroku

This repository contains code to deploy [Apache Airflow](https://airflow.apache.org/) on [heroku](https://id.heroku.com/login). 
In airflow, multiple jobs (DAGS) are used to scrape newspapers using the Python package [Newspaper3k](https://newspaper.readthedocs.io/en/latest/) and insert them into a [MongoDB](https://www.mongodb.com/cloud). 

## Initial setup

Step 1 is only required if you wish to run the scraping dags. If you instead prefer to run your own dags, start from step 2 

1) OPTIONAL Create an account here [MongoDB](https://www.mongodb.com/cloud)
    1) Create a user with Read/Write permissions
    1) Generate the connection string for this user
    1) Add the connection to the heroku_setup.sh here:
    
         `heroku config:set MONGO_DB= "HERE ADD YOUR MONGO DB CONNECTION STRING"`

1) Register an account on https://www.heroku.com/ 
1) Login to heroku via terminal ``heroku login ``
1) Configure and deploy airflow ``bash heroku_setup.sh``
1) Open ``heroku open``
1) Change the user pw 

## Updating the instance with new dags

1) Implement your dags in the dags folder 
2) Push your changes to master
3) `git push heroku master`

------------

As always, we did not reinvent the wheel, but benefited from multiple source out of which we can remember the following:

- Setting up airflow on heroku https://medium.com/@damesavram/running-airflow-on-heroku-ed1d28f8013d

