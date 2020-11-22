from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

user = PasswordUser(models.User())
user.username = 'admin'
user.email = 'YOUR@MAIL.com'
user.password = 'admin'
user.superuser = True
session = settings.Session()
session.add(user)
session.commit()
session.close()
exit()