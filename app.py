from SQLModels import postgre, Uzivatele, Role, Prispevky, Hodnoceni, Komentare, Odpovedi, uzivatele_role
from SQL import engine, createUser, deleteUser, listUsers, createRole, deleteRole, listRolesOfUser, listRoles, grant, revoke, showGrant, setRole, lockTable, listTables
from flask import Flask, render_template, request, session, flash, redirect, url_for
from sqlalchemy import func, create_engine
import hashlib
import decimal

data = []
path = ""
engineUser = "postgres"
flasksqlalchemy = True

flaskApp = Flask(__name__)
flaskApp.app_context().push()
flaskApp.secret_key = "16ecab1875791e2b6ed0c9a6dae5a12a79d92120e1c3afbd3a9c8535ce44660d"
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123@localhost:5432/forum"
#flaskApp.config['SQLALCHEMY_ECHO'] = True

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
        return "Nemáte dostatečná práva!"
    for data in query:
        for dat in data:
            finalList.append(dat)
    return finalList

def prispevekData(komentareQuery, obrazkyQuery, prispevekQuery, id, userid):
    komentare = []
    odpovedi = []
    obrazky = []
    komentareIDs = []
    rawOdpovedi = []
    prispevek = []
    userHodnoceni = ""
    rawKomentare = komentareQuery
    for prispev in prispevekQuery:
        pris = []
        for pri in prispev:
            pris.append(pri)
        prispevek.append(pris)
    prispevek = prispevek[0]
    for komentar in rawKomentare:
        comm = []
        for koment in komentar:
            comm.append(koment)
        komentareIDs.append(comm[0])
        komentare.append(comm)
    for odpoved in komentareIDs:
        if flasksqlalchemy:
            rawOdpovedi.append(postgre.session.query(Odpovedi.komentar_id, Odpovedi.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Odpovedi.komentar_id==odpoved).all())
        else:
            rawOdpovedi.append(postgreSQL.execute("SELECT o.komentar_id, o.text, u.prezdivka FROM odpovedi AS o LEFT JOIN komentare AS k ON o.komentar_id = k.id LEFT JOIN uzivatele AS u ON u.id = o.uzivatel_id WHERE k.id='{0}'".format(odpoved)))
    for rawOdpoved in rawOdpovedi:
        for odpoved in rawOdpoved:
            odpo = []
            for reply in odpoved:
                odpo.append(reply)
            odpovedi.append(odpo)
    rawObrazky = obrazkyQuery
    for obrazek in rawObrazky:
        for obraz in obrazek:
            obrazky.append(obraz)
    if flasksqlalchemy:
        userHodnoceni = postgre.session.query(Hodnoceni.hodnoceni).join(Prispevky).filter(Hodnoceni.uzivatel_id==userid).filter(Prispevky.id==id).scalar()
    else:
        userHodnoceni = str(postgreSQL.execute("SELECT h.hodnoceni FROM hodnoceni AS h LEFT JOIN uzivatele AS u ON u.id = h.uzivatel_id LEFT JOIN prispevky AS p ON p.id = h.prispevek_id WHERE h.uzivatel_id = '{0}' AND p.id = '{1}'".format(userid, id)).fetchone())
        if userHodnoceni:
            userHodnoceni = userHodnoceni[10:11]
    if flasksqlalchemy:
        hodnoceniavg = postgre.session.query(func.avg(Hodnoceni.hodnoceni)).join(Prispevky).filter(Prispevky.id==id).scalar()
    else:
        hodnoceniavg = str(postgreSQL.execute("SELECT AVG(h.hodnoceni) FROM prispevky AS p LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id WHERE p.id = {0}".format(id)).fetchone()[0])
    hodnoceniavg = str(hodnoceniavg)[0:3]
    return prispevek, komentare, odpovedi, obrazky, userHodnoceni, hodnoceniavg

def role(session):
    username = session.get("username")
    if username:
        if flasksqlalchemy:
            list = postgre.session.query(Role.id).join(Uzivatele, Role.roles).filter(Uzivatele.prezdivka==username).all()
        else:
            list = postgreSQL.execute("SELECT r.id FROM role AS r LEFT JOIN uzivatele_role AS ur ON r.id = ur.role_id LEFT JOIN uzivatele AS u ON ur.uzivatel_id = u.id WHERE u.prezdivka = '{0}'".format(username))
        highest = 0
        for rolelist in list:
            for role in rolelist:
                if int(role) > highest:
                    highest = int(role)
        if highest == 4:
            return "majitel"
        if highest == 3:
            return "admin"
        if highest == 2:
            return "moderátor"
        return "uživatel"
    return "x"

def hodnoceniList(id):
    finalList = []
    finalString = ""
    if flasksqlalchemy:
        list = postgre.session.query(Hodnoceni.hodnoceni, Uzivatele.prezdivka).join(Uzivatele).filter(Hodnoceni.prispevek_id == id).all()
    else:
        list = postgreSQL.execute("SELECT h.hodnoceni, u.prezdivka FROM uzivatele AS u LEFT JOIN hodnoceni AS h ON h.uzivatel_id = u.id LEFT JOIN prispevky AS p ON p.id = h.prispevek_id WHERE p.id = {0}".format(id)).fetchall()
    for hodnoceni in list:
        prezdivka = hodnoceni[1]
        hodnota = str(hodnoceni[0])
        finalList.append([prezdivka, hodnota])
    for hodnoceni in finalList:
        finalString = finalString + hodnoceni[0] + " - " + hodnoceni[1] + "\u000d"
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
            if flasksqlalchemy:
                if username not in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars() and email not in postgre.session.execute(postgre.select(Uzivatele.email)).scalars():
                    registrable = True
            else:
                if username not in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()) and email not in queryToList(postgreSQL.execute("SELECT email FROM uzivatele").fetchall()):
                    registrable = True 
            if registrable:
                hashed_pass = hashlib.sha256(request.form["password"].encode("utf-8")).hexdigest()
                if flasksqlalchemy:
                    register = Uzivatele(
                        prezdivka = request.form["username"],
                        heslo = hashed_pass,
                        email = request.form["email"]
                    )
                    postgre.session.add(register)
                    postgre.session.commit()
                else:
                    postgreSQL.execute("INSERT INTO uzivatele (prezdivka, heslo, email) VALUES ('{0}', '{1}', '{2}')".format(username, hashed_pass, email))
                if flasksqlalchemy:
                    id = postgre.session.execute(postgre.select(Uzivatele.id).where(Uzivatele.prezdivka==username)).scalar()
                    roleinsert = uzivatele_role.insert().values(role_id=1, uzivatel_id=id)
                    postgre.session.execute(roleinsert)
                    postgre.session.commit()
                else:
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
        return render_template("register.html", session=session, role=role(session))

@flaskApp.route("/forum", methods=["GET", "POST"])
def forum():
    if session.get("username"):
        if request.method == "GET":
            data.clear()
            if flasksqlalchemy:
                prispevek = []
                i=0
                rawdata = postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni)).select_from(Prispevky).join(Uzivatele).outerjoin(Hodnoceni, Prispevky.id==Hodnoceni.prispevek_id).group_by(Prispevky.id, Uzivatele.prezdivka).order_by(Prispevky.id).all()
                for prispevky in rawdata:
                    prispevek = []
                    for smalldata in prispevky:
                        if isinstance(smalldata, decimal.Decimal):
                            prispevek.append(str(smalldata)[0:3])
                        else:
                            prispevek.append(smalldata)
                    data.append(prispevek)
            else:
                rawdata = postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni) FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id GROUP BY p.id, u.prezdivka ORDER BY p.id").fetchall()
                prispevekid = 0
                for prispevek in range(0, int(len(rawdata))):
                    prispevek = []
                    for i in range(0,5):
                        if i == 4:
                            if str(rawdata[prispevekid][i]) == "None":
                                prispevek.append("")
                            else:
                                prispevek.append(str(rawdata[prispevekid][i])[0:3])
                        else:
                            prispevek.append(rawdata[prispevekid][i])
                        i = i + 1
                    prispevekid = prispevekid + 1
                    data.append(prispevek)
            print(data)
            return render_template("forum.html", session=session, role=role(session), data=data)
        return catchall(path)
    else:
        return redirect(url_for("index"))

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
            if flasksqlalchemy:
                if username in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars():
                    loggable = True
            else:
                if username in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()):
                    loggable = True
            if loggable:
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                if flasksqlalchemy:
                    if hashed_password == postgre.session.execute(postgre.select(Uzivatele.heslo).where(Uzivatele.prezdivka == username)).scalar():
                        loggedin = True
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
            if session.get("username"):
                session.pop("username")
            flash("logout")
            return render_template("index.html", session=session, role=role(session))
        elif request.form["btn"] == "flask":
            return catchall(path)
    return render_template("index.html", session=session, role=role(session))

@flaskApp.route("/forum/<id>", methods=["GET", "POST"])
def prispevek(id):
    if session.get("username"):
        for pris in data:
            if str(pris[0]) == id:
                prispevek = pris
        hodnoceni = hodnoceniList(id)
        if flasksqlalchemy:
            prispevek, komentare, odpovedi, obrazky, userHodnoceni, hodnoceniavg = prispevekData(postgre.session.query(Komentare.id, Komentare.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Komentare.prispevek_id==id).all(),postgre.session.query(Prispevky.obrazek).filter(Prispevky.id==id).all(), postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni)).select_from(Prispevky).join(Uzivatele).join(Hodnoceni).filter(Prispevky.id== id).group_by(Prispevky.id, Uzivatele.prezdivka), id, session["userid"])
            print("flasksqlalchemy")
        else:
            prispevek, komentare, odpovedi, obrazky, userHodnoceni, hodnoceniavg = prispevekData(postgreSQL.execute("SELECT k.id, k.text, u.prezdivka FROM komentare AS k LEFT JOIN uzivatele AS u ON u.id = k.uzivatel_id WHERE k.prispevek_id = '{0}'".format(id)).fetchall(),postgreSQL.execute("SELECT obrazek FROM prispevky WHERE id = {0}".format(id)),postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni) FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id WHERE p.id = '{0}' GROUP BY p.id, u.prezdivka".format(id)), id, session["userid"])
            print("sqlalchemy")
        if request.method == "GET":
            return render_template("prispevek.html", session=session, role=role(session), prispevek=prispevek, hodnoceni=hodnoceni, komentare=komentare, odpovedi=odpovedi, obrazky=obrazky, userHodnoceni=userHodnoceni)
        if request.method == "POST":
            if request.form["btn"] == "ohodnotit":
                hodnoceni = request.form.get("hodnoceniselect")
                if postgreSQL.execute("SELECT id FROM hodnoceni WHERE uzivatel_id = '{0}' AND prispevek_id = '{1}'".format(session["userid"], id)).fetchone() is None:
                    if flasksqlalchemy:
                        hodnota = Hodnoceni (
                            hodnoceni = hodnoceni,
                            uzivatel_id = session["userid"],
                            prispevek_id = id
                        )
                        postgre.session.add(hodnota)
                        postgre.session.commit()
                    else:
                        postgreSQL.execute("INSERT INTO hodnoceni (hodnoceni, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(hodnoceni, session["userid"], id))
                else:
                    if flasksqlalchemy:
                        hodnota = Hodnoceni.query.filter_by(prispevek_id = id).filter_by(uzivatel_id = session["userid"]).first()
                        hodnota.hodnoceni = hodnoceni
                        postgre.session.commit()
                    else:
                        postgreSQL.execute("UPDATE hodnoceni SET hodnoceni = '{0}' WHERE uzivatel_id = '{1}' AND prispevek_id = '{2}'".format(hodnoceni, session["userid"], id))
            elif request.form["btn"] == "addKomentar":
                komentartext = request.form.get("newkomentar")
                if komentartext != "":
                    if flasksqlalchemy:
                        koment = Komentare (
                            uzivatel_id = session["userid"],
                            prispevek_id = id,
                            text = komentartext
                        )
                        postgre.session.add(koment)
                        postgre.session.commit()
                    else:
                        postgreSQL.execute("INSERT INTO komentare (text, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(komentartext, session["userid"], id))
            elif request.form["btn"][0:10] == "addOdpoved":
                komentarid = request.form["btn"][10:]
                odpovedtext = request.form.get("newodpoved" + komentarid)
                if odpovedtext != "":
                    if flasksqlalchemy:
                        odpoved = Odpovedi (
                            uzivatel_id = session["userid"],
                            komentar_id = komentarid,
                            text = odpovedtext
                        )
                        postgre.session.add(odpoved)
                        postgre.session.commit()
                    else:
                        postgreSQL.execute("INSERT INTO odpovedi (text, uzivatel_id, komentar_id) VALUES ('{0}', '{1}', '{2}')".format(odpovedtext, session["userid"], komentarid))
            for pris in data:
                if str(pris[0]) == id:
                    prispevek = pris
            hodnoceni = hodnoceniList(id)
            if flasksqlalchemy:
                prispevek, komentare, odpovedi, obrazky, userHodnoceni, hodnoceniavg = prispevekData(postgre.session.query(Komentare.id, Komentare.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Komentare.prispevek_id==id).all(),postgre.session.query(Prispevky.obrazek).filter(Prispevky.id==id).all(), postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni)).select_from(Prispevky).join(Uzivatele).join(Hodnoceni).filter(Prispevky.id== id).group_by(Prispevky.id, Uzivatele.prezdivka), id, session["userid"])
            else:
                prispevek, komentare, odpovedi, obrazky, userHodnoceni, hodnoceniavg = prispevekData(postgreSQL.execute("SELECT k.id, k.text, u.prezdivka FROM komentare AS k LEFT JOIN uzivatele AS u ON u.id = k.uzivatel_id WHERE k.prispevek_id = '{0}'".format(id)).fetchall(),postgreSQL.execute("SELECT obrazek FROM prispevky WHERE id = {0}".format(id)),postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni) FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id WHERE p.id = '{0}' GROUP BY p.id, u.prezdivka".format(id)), id, session["userid"])
            if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("prispevek.html", session=session, role=role(session), prispevek=prispevek, hodnoceni=hodnoceni, komentare=komentare, odpovedi=odpovedi, obrazky=obrazky, userHodnoceni=userHodnoceni, hodnoceniavg=hodnoceniavg)
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
        if session["selectedtabulka"] == "":
            session["selectedtabulka"] = "role"
        finalusers = queryToList(listUsers("postgres", "123"))
        uzivatele = queryToList(listUsers(session["engineUser"], session["enginePass"]))
        roles = queryToList(listRoles(session["engineUser"], session["enginePass"]))
        rolesofuser = queryToList(listRolesOfUser(session["roleuser"], session["engineUser"], session["enginePass"]))
        privofuser = queryToList(showGrant(session["privuser"], session["engineUser"], session["enginePass"]))
        tabulky = queryToList(listTables(session["engineUser"], session["enginePass"]))
        tabulkydata = queryToList(lockTable(session["selectedtabulka"], session["engineUser"], session["enginePass"]))
        if request.method == "GET":
            return render_template("sql.html", session=session, role=role(session), users=finalusers, uzivatele=uzivatele, roles=roles, rolesofuser=rolesofuser, roleuser=session["roleuser"], privofuser=privofuser, privuser=session["privuser"], selectedtabulka=session["selectedtabulka"], tabulky=tabulky, tabulkydata=tabulkydata, engineUser=session["engineUser"])
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
            if request.form["btn"] == "changetabulka":
                selectedtabulka = request.form.get("tableselect")
                session["selectedtabulka"] = selectedtabulka
            finalusers = queryToList(listUsers("postgres", "123"))
            uzivatele = queryToList(listUsers(session["engineUser"], session["enginePass"]))
            roles = queryToList(listRoles(session["engineUser"], session["enginePass"]))
            rolesofuser = queryToList(listRolesOfUser(session["roleuser"], session["engineUser"], session["enginePass"]))
            privofuser = queryToList(showGrant(session["privuser"], session["engineUser"], session["enginePass"]))
            tabulkydata = queryToList(lockTable(session["selectedtabulka"], session["engineUser"], session["enginePass"]))
            if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("sql.html", session=session, role=role(session), users=finalusers, uzivatele=uzivatele, roles=roles, rolesofuser=rolesofuser, roleuser=session["roleuser"], privofuser=privofuser, privuser=session["privuser"], selectedtabulka=session["selectedtabulka"], tabulky=tabulky, tabulkydata=tabulkydata, engineUser=session["engineUser"])
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/new", methods=["GET", "POST"])
def new():
    if session.get("username"):
        if request.method == "GET":
            return render_template("new.html",session=session,role=role(session))
        if request.method == "POST":
            if request.form["btn"] == "addPrispevek":
                nazev = request.form.get("nazev")
                obsah = request.form.get("text")
                obrazek = request.form.get("obrazek")
                if obrazek == "":
                    obrazek = "NULL"
                if flasksqlalchemy:
                    prispevek = Prispevky(
                        nazev = nazev,
                        obsah = obsah,
                        obrazek = obrazek,
                        uzivatel_id = session["userid"]
                    )
                    postgre.session.add(prispevek)
                    postgre.session.commit()
                else:
                    postgreSQL.execute("INSERT INTO prispevky (nazev, obsah, obrazek, uzivatel_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(nazev, obsah, obrazek, session["userid"]))
                return redirect(url_for("forum"))
            return catchall(path)
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
            global flasksqlalchemy
            if flasksqlalchemy == True:
                flasksqlalchemy = False
                session["engine"] = "sqlalchemy"
            else:
                flasksqlalchemy = True
                session["engine"] = "flask-sqlalchemy"
            return redirect(request.referrer)

if __name__ == "__main__":
    flaskApp.run(debug=True, host="0.0.0.0")
