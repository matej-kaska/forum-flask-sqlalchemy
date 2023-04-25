from SQLModels import postgre, Uzivatele, Role, Prispevky, Hodnoceni, Komentare, Odpovedi, Uzivatele_audits, uzivatele_role
from SQL import engine, createUser, deleteUser, listUsers, createRole, deleteRole, listRolesOfUser, listRoles, grant, revoke, showGrant, setRole, lockTable, listTables
from flask import Flask, render_template, request, session, flash, redirect, url_for
from sqlalchemy import func, create_engine, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by
import hashlib
import decimal

data = []
path = ""
engineUser = "postgres"
orm_flasksqlalchemy = True

flaskApp = Flask(__name__)
flaskApp.app_context().push()
flaskApp.secret_key = "16ecab1875791e2b6ed0c9a6dae5a12a79d92120e1c3afbd3a9c8535ce44660d"
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123@localhost:5432/forum"
#flaskApp.config['SQLALCHEMY_ECHO'] = True      #SQL-alchemy debugger

#sql administration commands
""" createUser("matej", "123", "postgres", "123")
listUsers("postgres", "123")
createRole("matejr", "postgres", "123")
setRole("matejr", "matej", "postgres", "123")
grant("SELECT", "matejr", "postgres", "123")
showGrant("matej", "postgres", "123")
listRolesOfUser("matej", "postgres", "123")
listRoles("postgres", "123") 
revoke("SELECT", "matejr", "postgres", "123")
deleteRole("matejr", "postgres", "123")
deleteUser("matej", "postgres", "123") """

#flask-sqlalchemy session
postgre.init_app(flaskApp)
postgre.create_all()

#sqlalchemy session
postgreSQL = create_engine("postgresql://postgres:123@localhost:5432/forum")

def queryToList(query):
    finalList = []
    if query == None or query == "error":
        return "You dont have enough rights!"
    for data in query:
        for dat in data:
            finalList.append(dat)
    return finalList

def queryPostToList(query, id):
    final = []
    finalID = []
    for data in query:
        dat = []
        for da in data:
            dat.append(da)
        if id == True:
            finalID.append(dat[0])
        final.append(dat)
    if id == True:
        return final, finalID
    return final

def postData(commentsQuery, postQuery, userRatingQuery, id):
    answers = []
    rawAnswers = []
    post = queryPostToList(postQuery, False)
    comments, commentsIDs = queryPostToList(commentsQuery, True)
    if userRatingQuery == None:
        userRating = "1"
    else:
        try:
            userRating = str(int(userRatingQuery))
        except:
            userRating = str(int(userRatingQuery[0]))
    for answer in commentsIDs:
        # ===> Getting answers from comment <===
        # ---> orm-flask-sqlalchemy <---
        if orm_flasksqlalchemy:
            rawAnswers.append(postgre.session.query(Odpovedi.komentar_id, Odpovedi.text, Uzivatele.prezdivka, Odpovedi.id).outerjoin(Uzivatele).filter(Odpovedi.komentar_id==answer).order_by(Odpovedi.id).all())
        # ---> sql <---
        else:
            rawAnswers.append(postgreSQL.execute("SELECT o.komentar_id, o.text, u.prezdivka, o.id FROM odpovedi AS o LEFT JOIN komentare AS k ON o.komentar_id = k.id LEFT JOIN uzivatele AS u ON u.id = o.uzivatel_id WHERE k.id='{0}' ORDER BY o.id".format(answer)))
    for rawAnswer in rawAnswers:
        answer = queryPostToList(rawAnswer, False)
        if answer != []:
            for answ in answer:
                answers.append(answ)
    return post, comments, answers, userRating

def role(session):
    username = session.get("username")
    if username:
        # ===> Getting role of user <===
        # ---> orm-flask-sqlalchemy <---
        if orm_flasksqlalchemy:
            list = postgre.session.query(Role.id).join(Uzivatele.role).filter(Uzivatele.prezdivka==username).all()
        # ---> sql <---
        else:
            list = postgreSQL.execute("SELECT r.id FROM role AS r LEFT JOIN uzivatele_role AS ur ON r.id = ur.role_id LEFT JOIN uzivatele AS u ON ur.uzivatel_id = u.id WHERE u.prezdivka = '{0}'".format(username))
        highest = 0
        for rolelist in list:
            for role in rolelist:
                if int(role) > highest:
                    highest = int(role)
        if highest == 4:
            return "owner"
        if highest == 3:
            return "admin"
        if highest == 2:
            return "moderator"
        return "user"
    return "x"

def ratingList(id):
    finalList = []
    finalString = ""
    # ===> Getting list of all ratings of posts <===
    # ---> orm-flask-sqlalchemy <---
    if orm_flasksqlalchemy:
        list = postgre.session.query(Hodnoceni.hodnoceni, Uzivatele.prezdivka).join(Uzivatele).filter(Hodnoceni.prispevek_id == id).all()
    # ---> sql <---
    else:
        list = postgreSQL.execute("SELECT h.hodnoceni, u.prezdivka FROM uzivatele AS u LEFT JOIN hodnoceni AS h ON h.uzivatel_id = u.id LEFT JOIN prispevky AS p ON p.id = h.prispevek_id WHERE p.id = {0}".format(id)).fetchall()
    for rating in list:
        username = rating[1]
        value = str(rating[0])
        finalList.append([username, value])
    for rating in finalList:
        finalString = finalString + rating[0] + " - " + rating[1] + "\u000d" # Next line
    return finalString

@flaskApp.before_first_request
def load_user():
    session["engine"] = "flask-sqlalchemy"

@flaskApp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("username"):
        return redirect(url_for("forum"))
    if request.method == "GET":
        return render_template("register.html", session=session, role=role(session))
    elif request.method == "POST":
        if request.form["btn"] == "register":
            username = request.form["username"]
            email = request.form["email"]
            registrable = False
            # ===> Finding out if a nickname or email is already in the database <===
            # ---> orm-flask-sqlalchemy <---
            if orm_flasksqlalchemy:
                if username not in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars() and email not in postgre.session.execute(postgre.select(Uzivatele.email)).scalars():
                    registrable = True
            # ---> sql <---
            else:
                if username not in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()) and email not in queryToList(postgreSQL.execute("SELECT email FROM uzivatele").fetchall()):
                    registrable = True 
            if registrable:
                hashed_pass = hashlib.sha256(request.form["password"].encode("utf-8")).hexdigest()
                # ===> Adding a user to the database <===
                # ---> orm-flask-sqlalchemy <---
                if orm_flasksqlalchemy:
                    register = Uzivatele(
                        prezdivka = request.form["username"],
                        heslo = hashed_pass,
                        email = request.form["email"]
                    )
                    postgre.session.add(register)
                    postgre.session.commit()
                    id = postgre.session.execute(postgre.select(Uzivatele.id).where(Uzivatele.prezdivka==username)).scalar()
                    roleinsert = uzivatele_role.insert().values(role_id=1, uzivatel_id=id)
                    postgre.session.execute(roleinsert)
                    postgre.session.commit()
                # ---> sql <---
                else:
                    postgreSQL.execute("INSERT INTO uzivatele (prezdivka, heslo, email) VALUES ('{0}', '{1}', '{2}')".format(username, hashed_pass, email))
                    id = postgreSQL.execute("SELECT id FROM uzivatele WHERE prezdivka = '{0}'".format(username)).fetchone()
                    postgreSQL.execute("INSERT INTO uzivatele_role (role_id, uzivatel_id) VALUES ('1', '{0}')".format(id[0]))
                id =  postgreSQL.execute("SELECT id FROM uzivatele WHERE prezdivka = '{0}'".format(username)).fetchone()[0]
                session["username"] = request.form["username"]
                session["userid"] = id
                session["engineUser"] = "postgres"
                session["enginePass"] = "123"
                session["roleuser"] = ""
                session["privuser"] = ""
                session["selectedtabulka"] = ""
                flash("regsucces")
                return redirect(url_for("forum"))
            else:
                flash("regerror")
                return redirect(request.referrer) 
        elif request.form["btn"] == "flask":
            return catchall(path)
        return render_template("register.html", session=session, role=role(session))

@flaskApp.route("/", methods=["GET", "POST"])
def index():
    if session.get("username"):
        return redirect(url_for("forum"))
    if request.method == "GET":
        return render_template("index.html", session=session, role=role(session))
    elif request.method == "POST":
        if request.form["btn"] == "login":
            username = request.form["username"]
            password = request.form["password"]
            loggable = False
            loggedin = False
            # ===> Finding out if user exists <===
            # ---> orm-flask-sqlalchemy <---
            if orm_flasksqlalchemy:
                if username in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars():
                    loggable = True
            # ---> sql <---
            else:
                if username in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()):
                    loggable = True
            if loggable:
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                # ===> Getting password of user <===
                # ---> orm-flask-sqlalchemy <---
                if orm_flasksqlalchemy:
                    if hashed_password == postgre.session.execute(postgre.select(Uzivatele.heslo).where(Uzivatele.prezdivka == username)).scalar():
                        loggedin = True
                # ---> sql <---
                else:
                    if hashed_password == postgreSQL.execute("SELECT heslo FROM uzivatele WHERE prezdivka = '{0}'".format(username)).fetchone()[0]:
                        loggedin = True
                if loggedin:
                    id =  postgreSQL.execute("SELECT id FROM uzivatele WHERE prezdivka = '{0}'".format(username)).fetchone()[0]
                    session["username"] = request.form["username"]
                    session["userid"] = id
                    session["engineUser"] = "postgres"
                    session["enginePass"] = "123"
                    session["roleuser"] = ""
                    session["privuser"] = ""
                    session["selectedtabulka"] = ""
                    flash("loginsucces")
                    return redirect(request.referrer)  
                else:
                    flash("loginerror")
                    return redirect(request.referrer)    
            else:
                flash("loginerror")
                return redirect(request.referrer)    
        elif request.form["btn"] == "logout":
            return catchall(path)
        elif request.form["btn"] == "flask":
            return catchall(path)
    return render_template("index.html", session=session, role=role(session))

@flaskApp.route("/forum", methods=["GET", "POST"])
def forum():
    if session.get("username"):
        if request.method == "GET":
            data.clear()
            # ===> Getting all posts <===
            # ---> orm-flask-sqlalchemy <---
            if orm_flasksqlalchemy:
                rawPosts = postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni)).select_from(Prispevky).join(Uzivatele).outerjoin(Hodnoceni, Prispevky.id==Hodnoceni.prispevek_id).group_by(Prispevky.id, Uzivatele.prezdivka).order_by(Prispevky.id).all()
            # ---> sql <---
            else:
                rawPosts = postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni) FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id GROUP BY p.id, u.prezdivka ORDER BY p.id").fetchall()
            for posts in rawPosts:
                post = []
                for smalldata in posts:
                    if isinstance(smalldata, decimal.Decimal):
                        post.append(str(smalldata)[0:3])
                    elif smalldata == None:
                        post.append("")
                    else:
                        post.append(smalldata)
                data.append(post)
            return render_template("forum.html", session=session, role=role(session), data=data)
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/<id>", methods=["GET", "POST"])
def post(id):
    if session.get("username"):
        if request.method == "POST":
            if request.form["btn"] == "rate":
                rating = request.form.get("rateGet")
                if postgreSQL.execute("SELECT id FROM hodnoceni WHERE uzivatel_id = '{0}' AND prispevek_id = '{1}'".format(session["userid"], id)).fetchone() is None:
                    # ===> Add rating to post <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        value = Hodnoceni (
                            hodnoceni = rating,
                            uzivatel_id = session["userid"],
                            prispevek_id = id
                        )
                        postgre.session.add(value)
                        postgre.session.commit()
                    # ---> sql <--
                    else:
                        postgreSQL.execute("INSERT INTO hodnoceni (hodnoceni, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(rating, session["userid"], id))
                else:
                    # ===> Change rating <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        value = Hodnoceni.query.filter_by(prispevek_id = id).filter_by(uzivatel_id = session["userid"]).first()
                        value.hodnoceni = rating
                        postgre.session.commit()
                    # ---> sql <--
                    else:
                        postgreSQL.execute("UPDATE hodnoceni SET hodnoceni = '{0}' WHERE uzivatel_id = '{1}' AND prispevek_id = '{2}'".format(rating, session["userid"], id))
            elif request.form["btn"] == "addComment":
                commentText = request.form.get("newComment")
                if commentText != "":
                    # ===> Add comment <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        comment = Komentare (
                            uzivatel_id = session["userid"],
                            prispevek_id = id,
                            text = commentText
                        )
                        postgre.session.add(comment)
                        postgre.session.commit()
                    # ---> sql <--
                    else:
                        postgreSQL.execute("INSERT INTO komentare (text, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(commentText, session["userid"], id))
            elif request.form["btn"][0:10] == "addAnswer":
                commentID = request.form["btn"][10:]
                answerText = request.form.get("newAnswer" + commentID)
                if answerText != "":
                    # ===> Adding answer to comment <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        answer = Odpovedi (
                            uzivatel_id = session["userid"],
                            komentar_id = commentID,
                            text = answerText
                        )
                        postgre.session.add(answer)
                        postgre.session.commit()
                    # ---> sql <--
                    else:
                        postgreSQL.execute("INSERT INTO odpovedi (text, uzivatel_id, komentar_id) VALUES ('{0}', '{1}', '{2}')".format(answerText, session["userid"], commentID))
            elif request.form["btn"] == "removePost":
                if role(session) != "moderator":
                    # ===> Removing post, comments, answers and ratings <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        answers = Odpovedi.query.outerjoin(Komentare).outerjoin(Prispevky, Komentare.prispevek_id==Prispevky.id).filter(Prispevky.id == id).all()
                        for answer in answers:
                            postgre.session.delete(answer)
                            postgre.session.commit()
                        Hodnoceni.query.filter(Hodnoceni.prispevek_id == id).delete()
                        Komentare.query.filter(Komentare.prispevek_id == id).delete()
                        Prispevky.query.filter(Prispevky.id == id).delete()
                        postgre.session.commit()
                    # ---> sql <--
                    else:
                        postgreSQL.execute("DELETE FROM hodnoceni WHERE prispevek_id = {0};".format(id))
                        postgreSQL.execute("DELETE FROM odpovedi AS o USING komentare AS k, prispevky AS p WHERE o.komentar_id = k.id AND k.prispevek_id = p.id AND p.id = {0}".format(id))
                        postgreSQL.execute("DELETE FROM komentare WHERE prispevek_id = {0};".format(id))
                        postgreSQL.execute("DELETE FROM prispevky WHERE id = {0};".format(id))
                    return redirect(url_for("forum"))
            elif request.form["btn"][0:14] == "removeComment":
                commentID = request.form["btn"][14:]
                # ===> Removing comments and answers <===
                # ---> orm-flask-sqlalchemy <--
                if orm_flasksqlalchemy:
                    Odpovedi.query.filter(Odpovedi.komentar_id == commentID).delete()
                    Komentare.query.filter(Komentare.id == commentID).delete()
                    postgre.session.commit()
                # ---> sql <--
                else:
                    postgreSQL.execute("DELETE FROM odpovedi WHERE komentar_id = {0};".format(commentID))
                    postgreSQL.execute("DELETE FROM komentare WHERE id = {0};".format(commentID))
            elif request.form["btn"][0:13] == "removeAnswer":
                answerID = request.form["btn"][13:]
                # ===> Removing answer <===
                # ---> orm-flask-sqlalchemy <--
                if orm_flasksqlalchemy:
                    Odpovedi.query.filter(Odpovedi.id == answerID).delete()
                    postgre.session.commit()
                # ---> sql <--
                else:
                    postgreSQL.execute("DELETE FROM odpovedi WHERE id = {0};".format(answerID))
        for posts in data:
            if str(posts[0]) == id:
                post = posts
        rating = ratingList(id)
        # ===> Getting all post data <===
        # ---> orm-flask-sqlalchemy <--
        if orm_flasksqlalchemy:
            commentQuery = postgre.session.query(Komentare.id, Komentare.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Komentare.prispevek_id==id).all()
            postQuery = postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni), Prispevky.obrazek).select_from(Prispevky).join(Uzivatele).outerjoin(Hodnoceni, Prispevky.id==Hodnoceni.prispevek_id).filter(Prispevky.id== id).group_by(Prispevky.id, Uzivatele.prezdivka)
            userRatingQuery = postgre.session.query(Hodnoceni.hodnoceni).join(Prispevky).filter(Hodnoceni.uzivatel_id==session["userid"]).filter(Prispevky.id==id).scalar()
            post, comments, answers, userRating = postData(commentQuery, postQuery, userRatingQuery, id)
        # ---> sql <--
        else:
            commentQuery = postgreSQL.execute("SELECT k.id, k.text, u.prezdivka FROM komentare AS k LEFT JOIN uzivatele AS u ON u.id = k.uzivatel_id WHERE k.prispevek_id = '{0}'".format(id)).fetchall()
            postQuery = postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni), p.obrazek FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id WHERE p.id = '{0}' GROUP BY p.id, u.prezdivka".format(id))
            userRatingQuery = postgreSQL.execute("SELECT h.hodnoceni FROM hodnoceni AS h LEFT JOIN uzivatele AS u ON u.id = h.uzivatel_id LEFT JOIN prispevky AS p ON p.id = h.prispevek_id WHERE h.uzivatel_id = '{0}' AND p.id = '{1}'".format(session["userid"], id)).first()
            post, comments, answers, userRating = postData(commentQuery, postQuery, userRatingQuery, id)
        if request.method == "GET":
            return render_template("post.html", session=session, role=role(session), post=post, rating=rating, comments=comments, answers=answers, userRating=userRating)
        if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("post.html", session=session, role=role(session), post=post, rating=rating, comments=comments, answers=answers, userRating=userRating)
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/sql", methods=["GET", "POST"])
def sql():
    if session.get("username"):
        if session["roleuser"] == "":
            session["roleuser"] = session["engineUser"]
        if session["privuser"] == "":
            session["privuser"] = session["engineUser"]
        if session["selectedtable"] == "":
            session["selectedtable"] = "role"
        finalusers = queryToList(listUsers("postgres", "123"))
        users = queryToList(listUsers(session["engineUser"], session["enginePass"]))
        roles = queryToList(listRoles(session["engineUser"], session["enginePass"]))
        rolesofuser = queryToList(listRolesOfUser(session["roleuser"], session["engineUser"], session["enginePass"]))
        privofuser = queryToList(showGrant(session["privuser"], session["engineUser"], session["enginePass"]))
        tables = queryToList(listTables(session["engineUser"], session["enginePass"]))
        tabledata = queryToList(lockTable(session["selectedtable"], session["engineUser"], session["enginePass"]))
        if request.method == "GET":
            return render_template("sql.html", session=session, role=role(session), engineusers=finalusers, users=users, roles=roles, rolesofuser=rolesofuser, roleuser=session["roleuser"], privofuser=privofuser, privuser=session["privuser"], selectedtable=session["selectedtable"], tables=tables, tabledata=tabledata, engineUser=session["engineUser"])
        if request.method == "POST":
            if request.form["btn"] == "changeuser":
                if engine(request.form.get("userselect"), request.form.get("changeuserpass")) != "wrongpass":
                    session["enginePass"] = request.form.get("changeuserpass")
                    session["engineUser"] = request.form.get("userselect")
                else:
                    flash("engineerror")
            if request.form["btn"] == "createuser":
                username = request.form.get("createuserinputname")
                password = request.form.get("createuserinputpass")
                if username != "" and password != "":
                    if createUser(username, password, session["engineUser"], session["enginePass"]) == "error":
                        flash("createerror")
                else:
                    flash("createerror")
            if request.form["btn"] == "deleteuser":
                username = request.form.get("deleteuserinputname")
                if username != "":
                    if deleteUser(username, session["engineUser"], session["enginePass"]) == "error":
                        flash("deleteerror")
                else:
                    flash("deleteerror")
            if request.form["btn"] == "createrole":
                name = request.form.get("createroleinput")
                if name != "":
                    if createRole(name, session["engineUser"], session["enginePass"]) == "error":
                        flash("createerrorrole")
                else:
                    flash("createerrorrole")
            if request.form["btn"] == "deleterole":
                name = request.form.get("deleteroleinput")
                if name != "":
                    if deleteRole(name, session["engineUser"], session["enginePass"]) == "error":
                        flash("deleteerrorrole")
                else:
                    flash("deleteerrorrole")
            if request.form["btn"] == "grantrole":
                name = request.form.get("grantroleuser")
                rol = request.form.get("grantrolerole")
                if name != "" and rol != "":
                    if setRole(rol, name, session["engineUser"], session["enginePass"]) == "error":
                        flash("granterrorrole")
                else:
                    flash("granterrorrole")
            if request.form["btn"] == "changerole":
                roleuser = request.form.get("roleselect")
                session["roleuser"] = roleuser
            if request.form["btn"] == "grantbutton":
                name = request.form.get("grantuser")
                method = request.form.get("grantmethod")
                if name != "" and method != "":
                    if grant(method, name, session["engineUser"], session["enginePass"]) == "error":
                        flash("granterror")
                else:
                    flash("granterror")
            if request.form["btn"] == "revokebutton":
                name = request.form.get("revokeuser")
                method = request.form.get("revokemethod")
                if name != "" and method != "":
                    if revoke(method, name, session["engineUser"], session["enginePass"]) == "error":
                        flash("revokeerror")
                else:
                    flash("revokeerror")
            if request.form["btn"] == "changeprivuser":
                privuser = request.form.get("privuserselect")
                session["privuser"] = privuser
            if request.form["btn"] == "changetable":
                selectedtable = request.form.get("tableselect")
                session["selectedtable"] = selectedtable
            finalusers = queryToList(listUsers("postgres", "123"))
            users = queryToList(listUsers(session["engineUser"], session["enginePass"]))
            roles = queryToList(listRoles(session["engineUser"], session["enginePass"]))
            rolesofuser = queryToList(listRolesOfUser(session["roleuser"], session["engineUser"], session["enginePass"]))
            privofuser = queryToList(showGrant(session["privuser"], session["engineUser"], session["enginePass"]))
            tabledata = queryToList(lockTable(session["selectedtable"], session["engineUser"], session["enginePass"]))
            if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("sql.html", session=session, role=role(session), engineusers=finalusers, users=users, roles=roles, rolesofuser=rolesofuser, roleuser=session["roleuser"], privofuser=privofuser, privuser=session["privuser"], selectedtable=session["selectedtable"], tables=tables, tabledata=tabledata, engineUser=session["engineUser"])
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/new", methods=["GET", "POST"])
def new():
    if session.get("username"):
        if request.method == "GET":
            return render_template("new.html",session=session,role=role(session))
        if request.method == "POST":
            if request.form["btn"] == "addPost":
                title = request.form.get("title")
                text = request.form.get("text")
                picture = request.form.get("picture")
                if picture == "":
                    picture = "NULL"
                # ===> Adding post <===
                # ---> orm-flask-sqlalchemy <---
                if orm_flasksqlalchemy:
                    post = Prispevky(
                        nazev = title,
                        obsah = text,
                        obrazek = picture,
                        uzivatel_id = session["userid"]
                    )
                    postgre.session.add(post)
                    postgre.session.commit()
                # ---> sql <---
                else:
                    postgreSQL.execute("INSERT INTO prispevky (nazev, obsah, obrazek, uzivatel_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(title, text, picture, session["userid"]))
                return redirect(url_for("forum"))
            return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/roles", methods=["GET", "POST"])
def rolesWeb():
    if session.get("username"):
        if role(session) == "owner":
            if request.method == "POST":
                if request.form["btn"] == "changerole":
                    changedUser = request.form.get("userselect")
                    changedRole = request.form.get("roleselect")
                    # ===> Getting ID of user and his roles <===
                    # ---> orm-flask-sqlalchemy <--
                    if orm_flasksqlalchemy:
                        changedUserID = postgre.session.query(Uzivatele.id).filter(Uzivatele.prezdivka==changedUser).scalar()
                        oldRole = postgre.session.query(func.max(Role.id)).join(uzivatele_role).join(Uzivatele).filter(Uzivatele.id==changedUserID).scalar()
                    # ---> sql <--
                    else:
                        changedUserID = str(postgreSQL.execute("SELECT id FROM uzivatele WHERE prezdivka = '{0}'".format(changedUser)).fetchone()[0])
                        oldRole = str(postgreSQL.execute("SELECT MAX(role_id) FROM uzivatele_role WHERE uzivatel_id = '{0}'".format(changedUserID)).fetchone()[0])
                    if oldRole != "4":
                        # ===> Change user's role <===
                        # ---> orm-flask-sqlalchemy <--
                        if orm_flasksqlalchemy:
                            if int(oldRole) > int(changedRole):
                                oldRoles = postgre.session.query(Uzivatele).get(changedUserID)
                                oldRoles.role = []     
                                postgre.session.commit()                   
                                roleinsert = uzivatele_role.insert().values(uzivatel_id=changedUserID,role_id=1)
                                postgre.session.execute(roleinsert)
                                postgre.session.commit()
                            if int(changedRole) == 2 and int(changedRole) != int(oldRole):
                                roleinsert = uzivatele_role.insert().values(uzivatel_id=changedUserID,role_id=2)
                                postgre.session.execute(roleinsert)
                                postgre.session.commit()
                            if int(changedRole) == 3 and int(changedRole) != int(oldRole):
                                if int(oldRole) == 1:
                                    roleinsert = uzivatele_role.insert().values(uzivatel_id=changedUserID,role_id=2)
                                    postgre.session.execute(roleinsert)
                                roleinsert = uzivatele_role.insert().values(uzivatel_id=changedUserID,role_id=3)
                                postgre.session.execute(roleinsert)
                                postgre.session.commit()
                        # ---> sql <--
                        else:
                            if int(oldRole) > int(changedRole):
                                postgreSQL.execute("DELETE FROM uzivatele_role WHERE uzivatel_id = '{0}'".format(changedUserID))
                                postgreSQL.execute("INSERT INTO uzivatele_role (uzivatel_id, role_id) VALUES ('{0}','{1}')".format(changedUserID, 1))
                            if int(changedRole) == 2 and int(changedRole) != int(oldRole):
                                postgreSQL.execute("INSERT INTO uzivatele_role (uzivatel_id, role_id) VALUES ('{0}','{1}')".format(changedUserID, 2))
                            if int(changedRole) == 3 and int(changedRole) != int(oldRole):
                                if int(oldRole) == 1:
                                    postgreSQL.execute("INSERT INTO uzivatele_role (uzivatel_id, role_id) VALUES ('{0}','{1}')".format(changedUserID, 2))
                                postgreSQL.execute("INSERT INTO uzivatele_role (uzivatel_id, role_id) VALUES ('{0}','{1}')".format(changedUserID, 3))
                    else:
                        flash("ownererror")
            # ===> Getting all users and their roles <===
            # ---> orm-flask-sqlalchemy <--
            if orm_flasksqlalchemy:
                users = postgre.session.query(Uzivatele.prezdivka, func.string_agg(Role.nazev, aggregate_order_by(literal_column("', '"), Role.id))).select_from(uzivatele_role).join(Role).outerjoin(Uzivatele).group_by(Uzivatele.prezdivka, Uzivatele.id).order_by(Uzivatele.id).all()
            # ---> sql <--
            else:
                users = postgreSQL.execute("SELECT u.prezdivka, string_agg(r.nazev::character varying, ', ' order by r.id) FROM uzivatele_role AS ur LEFT JOIN uzivatele AS u ON u.id = ur.uzivatel_id LEFT JOIN role AS r ON r.id = ur.role_id GROUP BY u.prezdivka, u.id ORDER BY u.id").fetchall()
            if request.method == "GET":
                return render_template("roles.html",session=session,role=role(session),users=users)
            if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("roles.html",session=session,role=role(session),users=users)
            return catchall(path)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/account", methods=["GET", "POST"])
def account():
    if session.get("username"):
        if request.method == "POST":
            if request.form["btn"] == "changeDetails":
                changedEmail = request.form.get("changeEmailinput")
                changedPassword = request.form.get("changePasswordinput")
                # ===> Change email and password of user <===
                # ---> orm-flask-sqlalchemy <--
                if orm_flasksqlalchemy:
                    if changedEmail != "":
                        if changedEmail not in queryToList(postgre.session.query(Uzivatele.email).all()):
                            email = Uzivatele.query.filter_by(id = session["userid"]).first()
                            email.email = changedEmail
                            postgre.session.commit()
                        else:
                            flash("changeerror")
                    if changedPassword != "":
                        hashed_pass = hashlib.sha256(changedPassword.encode("utf-8")).hexdigest()
                        user = Uzivatele.query.filter_by(id = session["userid"]).first()
                        user.heslo = hashed_pass
                        postgre.session.commit()
                # ---> sql <--
                else:
                    if changedEmail != "":
                        if changedEmail not in queryToList(postgreSQL.execute("SELECT email FROM uzivatele").fetchall()):
                            postgreSQL.execute("UPDATE uzivatele SET email = '{0}' WHERE id = '{1}'".format(changedEmail, session["userid"]))
                        else:
                            flash("changeerror")
                    if changedPassword != "":
                        hashed_pass = hashlib.sha256(changedPassword.encode("utf-8")).hexdigest()
                        postgreSQL.execute("UPDATE uzivatele SET heslo = '{0}' WHERE id = '{1}'".format(hashed_pass, session["userid"]))
            if request.form["btn"] == "deleteAccount":
                # ===> Removing user, their posts, comments, answers and ratings <===
                # ---> orm-flask-sqlalchemy <--
                if orm_flasksqlalchemy:
                    deletedRoles = postgre.session.query(Uzivatele).get(session["userid"])
                    deletedRoles.role = []     
                    postgre.session.commit()
                    Hodnoceni.query.filter(Hodnoceni.uzivatel_id == session["userid"]).delete()
                    Odpovedi.query.filter(Odpovedi.uzivatel_id == session["userid"]).delete()
                    Komentare.query.filter(Komentare.uzivatel_id == session["userid"]).delete()
                    Prispevky.query.filter(Prispevky.uzivatel_id == session["userid"]).delete()
                    Uzivatele.query.filter(Uzivatele.id == session["userid"]).delete()
                    postgre.session.commit()
                # ---> sql <--
                else:
                    postgreSQL.execute("DELETE FROM hodnoceni WHERE uzivatel_id = {0};".format(session["userid"]))
                    postgreSQL.execute("DELETE FROM odpovedi WHERE uzivatel_id = {0};".format(session["userid"]))
                    postgreSQL.execute("DELETE FROM komentare WHERE uzivatel_id = {0};".format(session["userid"]))
                    postgreSQL.execute("DELETE FROM prispevky WHERE uzivatel_id = {0};".format(session["userid"]))
                    postgreSQL.execute("DELETE FROM uzivatele_role WHERE uzivatel_id = {0};".format(session["userid"]))
                    postgreSQL.execute("DELETE FROM uzivatele WHERE id = {0};".format(session["userid"]))
                session.pop("username")
                flash("logout")
                return redirect(url_for("index"))
        # ===> Getting user's info <===
        # ---> orm-flask-sqlalchemy <--
        if orm_flasksqlalchemy:
            user = postgre.session.query(Uzivatele.prezdivka, Uzivatele.email, Uzivatele.heslo).filter(Uzivatele.prezdivka==session["username"]).all()[0]
        # ---> sql <--
        else:
            user = postgreSQL.execute("SELECT prezdivka, email, heslo FROM uzivatele WHERE prezdivka = '{0}';".format(session["username"])).fetchall()[0]
        if request.method == "GET":
            return render_template("account.html",session=session,role=role(session),user=user)
        if request.form["btn"] != "logout":
            if request.form["btn"] != "flask":
                return render_template("account.html",session=session,role=role(session),user=user)
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/audits", methods=["GET", "POST"])
def audits():
    if session.get("username"):
        if role(session) == "owner":
            if request.method == "GET":
                # ===> Getting data from uzivatele_audits <===
                # ---> orm-flask-sqlalchemy <--
                if orm_flasksqlalchemy:
                    audits = postgre.session.query(Uzivatele_audits.uzivatel_id, Uzivatele_audits.prezdivka, Uzivatele_audits.email, Uzivatele_audits.heslo, Uzivatele_audits.zmena).all()
                # ---> sql <-
                else:
                    audits = postgreSQL.execute("SELECT uzivatel_id, prezdivka, email, heslo, zmena FROM uzivatele_audits").fetchall()
                return render_template("audits.html",session=session,role=role(session),audits=audits)
            return catchall(path)
        else:
            return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

@flaskApp.route('/<path:path>', methods=["POST"])
@flaskApp.route('/', defaults={'path': ''}, methods=["POST"])
def catchall(path):
    if request.method == "POST":
        if request.form["btn"] == "logout":
            session.pop("username")
            flash("logout")
            return redirect(url_for("index"))
        if request.form["btn"] == "flask":
            global orm_flasksqlalchemy
            if orm_flasksqlalchemy == True:
                orm_flasksqlalchemy = False
                session["engine"] = "sqlalchemy"
            else:
                orm_flasksqlalchemy = True
                session["engine"] = "flask-sqlalchemy"
            return redirect(request.referrer)

if __name__ == "__main__":
    flaskApp.run(debug=True, host="0.0.0.0")
