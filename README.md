![Banner]()

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

![Forum Screenshot]()

![Post Screenshot]()

![New post Screenshot]()

![User Screenshot]()

![Admin panel Screenshot]()

![Audits Screenshot]()

![SQL Screenshot]()

![Log in Screenshot]()

![Sign up Screenshot]()
