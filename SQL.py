from sqlalchemy import create_engine

def engine(username, password):
    try:
        sqlEngine = create_engine("postgresql://{0}:{1}@localhost:5432/forum".format(username,password))
        sqlEngine.execute("SELECT")
        return sqlEngine
    except Exception as e:
        print(e)
        return "wrongpass"

def createUser(username, password, engineUser, enginePassword):
    try:
        query = "CREATE USER {0} WITH PASSWORD '{1}';".format(username, password)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def deleteUser(username, engineUser, enginePassword):
    try:
        if username != "postgres":
            query = "DROP USER {0};".format(username)
            engine(engineUser, enginePassword).execute(query)
        else:
            return "Nelze smazat uživatele postgres!"
    except Exception as e:
        print(e)
        return "error"

def listUsers(engineUser, enginePassword):
    try:
        query = "SELECT pg.usename FROM pg_catalog.pg_user AS pg;"  
        listOfUsers=engine(engineUser, enginePassword).execute(query)
        return list(listOfUsers)
    except Exception as e:
        print(e)
        return "error"

def createRole(role, engineUser, enginePassword):
    try:
        query = "CREATE ROLE {0};".format(role)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def deleteRole(role, engineUser, enginePassword):
    try:
        query = "DROP ROLE {0};".format(role)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def setRole(role, username, engineUser, enginePassword):
    try:
        query = "GRANT {0} TO {1} ;".format(role, username)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def listRoles(engineUser, enginePassword):
    try:
        query = "SELECT rolname FROM pg_roles;"  
        listOfUsers=engine(engineUser, enginePassword).execute(query)
        return list(listOfUsers)
    except Exception as e:
        print(e)
        return "error"

def listRolesOfUser(username, engineUser, enginePassword):
    try:
        query = "SELECT rolname FROM pg_roles WHERE pg_has_role( '{0}', oid, 'member');".format(username)  
        listOfUsers=engine(engineUser, enginePassword).execute(query)
        return list(listOfUsers)
    except Exception as e:
        print(e)
        return "error"

def showGrant(username, engineUser, enginePassword):
    try:
        query = "SELECT DISTINCT privilege_type FROM information_schema.table_privileges AS tp WHERE grantee = '{0}'".format(username)
        listOfGrants = engine(engineUser, enginePassword).execute(query)
        return list(listOfGrants)
    except Exception as e:
        print(e)
        return "error"

def grant(metoda, username, engineUser, enginePassword):
    try:
        query = "GRANT {0} ON ALL TABLES IN SCHEMA public TO {1};".format(metoda,username)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def revoke(metoda, username, engineUser, enginePassword):
    try:
        query = "REVOKE {0} ON ALL TABLES IN SCHEMA public FROM {1};".format(metoda,username)
        engine(engineUser, enginePassword).execute(query)
    except Exception as e:
        print(e)
        return "error"

def lockTable(table, engineUser, enginePassword):
    try:
        engine(engineUser, enginePassword).begin()
        query = "LOCK TABLE {0} IN ACCESS SHARE MODE; SELECT * FROM {0}".format(table)
        table = engine(engineUser, enginePassword).execute(query)
        return table
    except Exception as e:
        print(e)
        return "error"

def listTables(engineUser, enginePassword):
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';"
        listOfTables = engine(engineUser, enginePassword).execute(query)
        return list(listOfTables)
    except Exception as e:
        print(e)
        return "error"