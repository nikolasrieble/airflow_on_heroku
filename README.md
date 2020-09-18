# airflow_on_heroku

1) Register an account on https://www.heroku.com/ 
2) Login to heroku via terminal ``heroku login ``
3) Configure and deploy airflow ``bash heroku_setup.sh``
4) Open ``heroku open``
5) Change the user pw 

based on 
https://medium.com/@damesavram/running-airflow-on-heroku-ed1d28f8013d

Deploy with new dag: 

`git push https://git.heroku.com/peaceful-waters-26909.git master`