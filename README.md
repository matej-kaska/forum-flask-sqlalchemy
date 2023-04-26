![Banner](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/forum-banner.png?raw=true)

# Forum flask-sqlalchemy

This is a basic Forum app built with Flask and PostgreSQL. The app provides users with the basic features like signing in, posting, rating or admin panel. It uses SQLAlchemy ORM models or you can use direct queries. It was my first project in Flask and HTML so there are a lot of clumsy CSS and code, so be ready.


## Tech 🛠

**Framework:** Flask

**Database:** PostgreSQL


## Features ✨

- Changing ORM query or SQL query (execute)
- Singing up
- Posting (with picture)
- Replying to posts and comments
- Rating
- Changing email or password
- User's audits
- Changing roles of users
- A lot of SQL commands (Creating users, roles, granting, revoking...)


## Installation 🔨

Clone my repository:

```bash
  git clone https://github.com/matej-kaska/forum-flask-sqlalchemy.git
```

Install packages (in root folder):

```bash
  pip install -r requirements.txt
```

Install PostgreSQL with pgAdmin:

https://ftp.postgresql.org/pub/pgadmin/pgadmin4/v7.0/windows/pgadmin4-7.0-x64.exe

Load SQL database:

	a) Create new database "forum"
	
	b) Right click -> "Restore" -> Select "forum.sql" in DB folder

(Optional) For czech version change branch to main-cz:

```bash
  git switch main-cz
```

Start (in root folder):

```bash
  & <path for python.exe> <path for app.py>
```

## Screenshots 🖥

![Forum Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-18-48.png?raw=true)

![Post Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-23-01.png?raw=true)

![New post Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-20-23.png?raw=true)

![User Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-19-37.png?raw=true)

![Admin panel Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-20-03.png?raw=true)

![Audits Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-19-05.png?raw=true)

![SQL Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-19-21.png?raw=true)

![Log in Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-17-32.png?raw=true)

![Sign up Screenshot](https://github.com/matej-kaska/forum-flask-sqlalchemy/blob/main/readme-assets/screenshot-2023-04-26-19-18-12.png?raw=true)
