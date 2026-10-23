========================================================================
                      DJANGO NEWS API CAPSTONE PROJECT
========================================================================

-------------------
1. PROJECT OVERVIEW
-------------------
This project is a comprehensive full-stack News and Content Management Portal
built with Django and Django REST Framework (DRF), backed by a MariaDB relational
database. It features strict Role-Based Access Control (RBAC), custom web dashboards
for readers, journalists, and editors, automated email notifications, and webhook
event handlers.

## GitHub Repository Link
You can access, fork, or clone the physical repository for testing and deployment
from your GitHub profile:
https://github.com/mcusick001/News-Application.git

-----------------
2. PREREQUISITES
-----------------
Make sure you have the following installed on your system:
 - Python (version 3.14.4)
 - MariaDB / MySQL server

--------------------
3. PROJECT STRUCTURE
--------------------
news_project/
│
├── news/
│   ├── migrations/
│   │   |-- __init__.py
│   │   |-- 0001_initial.py
|   |   |-- 0002_publisher_editors_publisher_journalists_and_more.py
|   |   |-- 0003_newsletter_articles.py
|   |   |-- 0004_alter_article_journalist.py
|   |   |-- 0005_alter_article_publisher.py
│   ├── templates/
│   │   └── news/
|   |       |-- article_confirm_delete.html
|   |       |-- article_feed.html
|   |       |-- article_form.html
│   │       |-- base.html
│   │       |-- editor_dashboard.html
│   │       |-- journalist_dashboard.html
│   │       |-- login.html
|   |       |-- newsletter_confirm_delete.html
│   │       |-- newsletter_form.html
│   │       |-- publisher_management.html
|   |       |-- reader_dashboard.html
│   │       |-- register.html
|   |       |-- subscriptions.html
│   ├── __init__.py
│   |-- admin.py
|   |-- api_urls.py
│   ├── api_views.py
│   ├── apps.py
│   ├── decorators.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py 
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── news_project/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt

-----------------------------
4. LOCAL SETUP & INSTALLATION
-----------------------------
1. Clone the repository and navigate into the project directory:
   ```bash

      git clone [https://github.com/mcusick001/NewsApplication.git]

      cd "NEW news_project"
   ```

2. Set Up a Virtual Environment & Install Dependencies
   ```bash
    
   python -m venv venv

   venv\Scripts\Activate.ps1

   pip install -r requirements.txt
   ```

3. Configure the Environmental Variables
   - Windows (Command Prompt):
   ```cmd

   copy .env.example .env
   ```
   - Open the newly created .env file in your code editor and update
     the database username, password, and secret key to match your
     local environment.

4. Log into your MariaDB shell and create the database:
   ```bash

   mysql -u root -p
   ```
   - Once logged in, run the following SQL commands to create the
     database and user:
   ```sql

   CREATE DATABASE news_db;
   CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'db_password';
   GRANT ALL PRIVILEGES ON news_db.* TO 'db_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ``` 

5. Run Database Migrations
   - Apply the Django schema to your MariaDB instance:
   ```bash:

   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create an Administrator (Superuser) Account
   ```bash:

   python manage.py createsuperuser
   ```
   - Follow the prompts to enter username, email, and password.

7. Run the deployment server
   ```bash:

   python manage.py runserver
   ```
   - Open your brower and navigate to [http://127.0.0.1:8000/]
     to use the application!

8. Accessing the application
   Once the server is running, you can open your web browser and access
   the application at the following endpoints:
   - Home/Login Page: http://127.0.0.1:8000/
   - User Registration: http://127.0.0.1:8000/register/
   - Smart Dashboard Routing: http://127.0.0.1:8000/dashboard/
   (Automatically routes you based on your user role after logging
   in)
   - Django Admin Panel: http://127.0.0.1:8000/admin/
   - REST API Root: http://127.0.0.1:8000/api/

-----------------------
5. AUTOMATED TEST SUITE
-----------------------
The project includes a robust unit test suite (`APITestCase`) in `news/tests.py`
covering authentication, RBAC permissions, webhook mocking, and subscription filtering.

To run the automated tests:
   ```bash

   python manage.py test news
   ```
