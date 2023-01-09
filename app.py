from SQLModels import postgre, Uzivatele, Role, Prispevky, Hodnoceni, Komentare, Odpovedi, uzivatele_role
from SQL import engine, createUser, deleteUser, listUsers, createRole, deleteRole, listRolesOfUser, listRoles, grant, revoke, showGrant, setRole, lockTable, listTables
from flask import Flask, render_template, request, session, flash, redirect, url_for
from sqlalchemy import func, create_engine, literal_column
from sqlalchemy.dialects.postgresql import aggregate_order_by
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
        return "Nemáte dostatečná práva!"
    for data in query:
        for dat in data:
            finalList.append(dat)
    return finalList

def queryPrispevekToList(query, id):
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

def prispevekData(komentareQuery, prispevekQuery, userhodnoceniQuery, id):
    odpovedi = []
    rawOdpovedi = []
    prispevek = queryPrispevekToList(prispevekQuery, False)
    komentare, komentareIDs = queryPrispevekToList(komentareQuery, True)
    if userhodnoceniQuery == None:
        userHodnoceni = "1"
    else:
        try:
            userHodnoceni = str(int(userhodnoceniQuery))
        except:
            userHodnoceni = str(int(userhodnoceniQuery[0]))
    for odpoved in komentareIDs:
        # ===> Získání odpovědí u komentářů <===
        # ---> flask-sqlalchemy <---
        if flasksqlalchemy:
            rawOdpovedi.append(postgre.session.query(Odpovedi.komentar_id, Odpovedi.text, Uzivatele.prezdivka, Odpovedi.id).outerjoin(Uzivatele).filter(Odpovedi.komentar_id==odpoved).order_by(Odpovedi.id).all())
        # ---> sqlalchemy <---
        else:
            rawOdpovedi.append(postgreSQL.execute("SELECT o.komentar_id, o.text, u.prezdivka, o.id FROM odpovedi AS o LEFT JOIN komentare AS k ON o.komentar_id = k.id LEFT JOIN uzivatele AS u ON u.id = o.uzivatel_id WHERE k.id='{0}' ORDER BY o.id".format(odpoved)))
    for rawOdpoved in rawOdpovedi:
        odpoved = queryPrispevekToList(rawOdpoved, False)
        if odpoved != []:
            for odpo in odpoved:
                odpovedi.append(odpo)
    return prispevek, komentare, odpovedi, userHodnoceni

def role(session):
    username = session.get("username")
    if username:
        # ===> Získání role uživatele <===
        # ---> flask-sqlalchemy <---
        if flasksqlalchemy:
            list = postgre.session.query(Role.id).join(Uzivatele.role).filter(Uzivatele.prezdivka==username).all()
        # ---> sqlalchemy <---
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
    # ===> Získání listu všech hodnocení u příspěvku <===
    # ---> flask-sqlalchemy <---
    if flasksqlalchemy:
        list = postgre.session.query(Hodnoceni.hodnoceni, Uzivatele.prezdivka).join(Uzivatele).filter(Hodnoceni.prispevek_id == id).all()
    # ---> sqlalchemy <---
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
            # ===> Zjištění, zda se přezdívka nebo e-mail se v databázi již nachází <===
            # ---> flask-sqlalchemy <---
            if flasksqlalchemy:
                if username not in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars() and email not in postgre.session.execute(postgre.select(Uzivatele.email)).scalars():
                    registrable = True
            # ---> sqlalchemy <---
            else:
                if username not in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()) and email not in queryToList(postgreSQL.execute("SELECT email FROM uzivatele").fetchall()):
                    registrable = True 
            if registrable:
                hashed_pass = hashlib.sha256(request.form["password"].encode("utf-8")).hexdigest()
                # ===> Přidání uživatele do databáze <===
                # ---> flask-sqlalchemy <---
                if flasksqlalchemy:
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
                # ---> sqlalchemy <---
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
            # ===> Zjištění, zda uživatel existuje <===
            # ---> flask-sqlalchemy <---
            if flasksqlalchemy:
                if username in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars():
                    loggable = True
            # ---> sqlalchemy <---
            else:
                if username in queryToList(postgreSQL.execute("SELECT prezdivka FROM uzivatele").fetchall()):
                    loggable = True
            if loggable:
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                # ===> Zjištění, hesla uživatele <===
                # ---> flask-sqlalchemy <---
                if flasksqlalchemy:
                    if hashed_password == postgre.session.execute(postgre.select(Uzivatele.heslo).where(Uzivatele.prezdivka == username)).scalar():
                        loggedin = True
                # ---> sqlalchemy <---
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
            # ===> Získání všech příspěvků <===
            # ---> flask-sqlalchemy <---
            if flasksqlalchemy:
                rawprispevky = postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni)).select_from(Prispevky).join(Uzivatele).outerjoin(Hodnoceni, Prispevky.id==Hodnoceni.prispevek_id).group_by(Prispevky.id, Uzivatele.prezdivka).order_by(Prispevky.id).all()
            # ---> sqlalchemy <---
            else:
                rawprispevky = postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni) FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id GROUP BY p.id, u.prezdivka ORDER BY p.id").fetchall()
            for prispevky in rawprispevky:
                prispevek = []
                for smalldata in prispevky:
                    if isinstance(smalldata, decimal.Decimal):
                        prispevek.append(str(smalldata)[0:3])
                    elif smalldata == None:
                        prispevek.append("")
                    else:
                        prispevek.append(smalldata)
                data.append(prispevek)
            return render_template("forum.html", session=session, role=role(session), data=data)
        return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/<id>", methods=["GET", "POST"])
def prispevek(id):
    if session.get("username"):
        if request.method == "POST":
            if request.form["btn"] == "ohodnotit":
                hodnoceni = request.form.get("hodnoceniselect")
                if postgreSQL.execute("SELECT id FROM hodnoceni WHERE uzivatel_id = '{0}' AND prispevek_id = '{1}'".format(session["userid"], id)).fetchone() is None:
                    # ===> Přidání hodnocení uživatelem <===
                    # ---> flask-sqlalchemy <--
                    if flasksqlalchemy:
                        hodnota = Hodnoceni (
                            hodnoceni = hodnoceni,
                            uzivatel_id = session["userid"],
                            prispevek_id = id
                        )
                        postgre.session.add(hodnota)
                        postgre.session.commit()
                    # ---> sqlalchemy <--
                    else:
                        postgreSQL.execute("INSERT INTO hodnoceni (hodnoceni, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(hodnoceni, session["userid"], id))
                else:
                    # ===> Změnění hodnocení uživatelem <===
                    # ---> flask-sqlalchemy <--
                    if flasksqlalchemy:
                        hodnota = Hodnoceni.query.filter_by(prispevek_id = id).filter_by(uzivatel_id = session["userid"]).first()
                        hodnota.hodnoceni = hodnoceni
                        postgre.session.commit()
                    # ---> sqlalchemy <--
                    else:
                        postgreSQL.execute("UPDATE hodnoceni SET hodnoceni = '{0}' WHERE uzivatel_id = '{1}' AND prispevek_id = '{2}'".format(hodnoceni, session["userid"], id))
            elif request.form["btn"] == "addKomentar":
                komentartext = request.form.get("newkomentar")
                if komentartext != "":
                    # ===> Přidání komentáře <===
                    # ---> flask-sqlalchemy <--
                    if flasksqlalchemy:
                        koment = Komentare (
                            uzivatel_id = session["userid"],
                            prispevek_id = id,
                            text = komentartext
                        )
                        postgre.session.add(koment)
                        postgre.session.commit()
                    # ---> sqlalchemy <--
                    else:
                        postgreSQL.execute("INSERT INTO komentare (text, uzivatel_id, prispevek_id) VALUES ('{0}', '{1}', '{2}')".format(komentartext, session["userid"], id))
            elif request.form["btn"][0:10] == "addOdpoved":
                komentarid = request.form["btn"][10:]
                odpovedtext = request.form.get("newodpoved" + komentarid)
                if odpovedtext != "":
                    # ===> Přidání odpovědi na komentář <===
                    # ---> flask-sqlalchemy <--
                    if flasksqlalchemy:
                        odpoved = Odpovedi (
                            uzivatel_id = session["userid"],
                            komentar_id = komentarid,
                            text = odpovedtext
                        )
                        postgre.session.add(odpoved)
                        postgre.session.commit()
                    # ---> sqlalchemy <--
                    else:
                        postgreSQL.execute("INSERT INTO odpovedi (text, uzivatel_id, komentar_id) VALUES ('{0}', '{1}', '{2}')".format(odpovedtext, session["userid"], komentarid))
            elif request.form["btn"] == "removePrispevek":
                if role(session) != "moderátor":
                    # ===> Odstranění příspěvku, komentářů, odpovědí a hodnocení <===
                    # ---> flask-sqlalchemy <--
                    if flasksqlalchemy:
                        odpovedi = Odpovedi.query.outerjoin(Komentare).outerjoin(Prispevky, Komentare.prispevek_id==Prispevky.id).filter(Prispevky.id == id).all()
                        for odpoved in odpovedi:
                            postgre.session.delete(odpoved)
                            postgre.session.commit()
                        Hodnoceni.query.filter(Hodnoceni.prispevek_id == id).delete()
                        Komentare.query.filter(Komentare.prispevek_id == id).delete()
                        Prispevky.query.filter(Prispevky.id == id).delete()
                        postgre.session.commit()
                    # ---> sqlalchemy <--
                    else:
                        postgreSQL.execute("DELETE FROM hodnoceni WHERE prispevek_id = {0};".format(id))
                        postgreSQL.execute("DELETE FROM odpovedi AS o USING komentare AS k, prispevky AS p WHERE o.komentar_id = k.id AND k.prispevek_id = p.id AND p.id = {0}".format(id))
                        postgreSQL.execute("DELETE FROM komentare WHERE prispevek_id = {0};".format(id))
                        postgreSQL.execute("DELETE FROM prispevky WHERE id = {0};".format(id))
                    return redirect(url_for("forum"))
            elif request.form["btn"][0:14] == "removeKomentar":
                komentarid = request.form["btn"][14:]
                # ===> Odstranění komentářů a odpovědí <===
                # ---> flask-sqlalchemy <--
                if flasksqlalchemy:
                    Odpovedi.query.filter(Odpovedi.komentar_id == komentarid).delete()
                    Komentare.query.filter(Komentare.id == komentarid).delete()
                    postgre.session.commit()
                # ---> sqlalchemy <--
                else:
                    postgreSQL.execute("DELETE FROM odpovedi WHERE komentar_id = {0};".format(komentarid))
                    postgreSQL.execute("DELETE FROM komentare WHERE id = {0};".format(komentarid))
            elif request.form["btn"][0:13] == "removeOdpoved":
                odpovedid = request.form["btn"][13:]
                # ===> Odstranění odpovědí <===
                # ---> flask-sqlalchemy <--
                if flasksqlalchemy:
                    Odpovedi.query.filter(Odpovedi.id == odpovedid).delete()
                    postgre.session.commit()
                # ---> sqlalchemy <--
                else:
                    postgreSQL.execute("DELETE FROM odpovedi WHERE id = {0};".format(odpovedid))
        for pris in data:
            if str(pris[0]) == id:
                prispevek = pris
        hodnoceni = hodnoceniList(id)
        # ===> Získání všech dat k příspěvku <===
        # ---> flask-sqlalchemy <--
        if flasksqlalchemy:
            komentareQuery = postgre.session.query(Komentare.id, Komentare.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Komentare.prispevek_id==id).all()
            prispevekQuery = postgre.session.query(Prispevky.id, Prispevky.obsah, Prispevky.nazev, Uzivatele.prezdivka, func.avg(Hodnoceni.hodnoceni), Prispevky.obrazek).select_from(Prispevky).join(Uzivatele).outerjoin(Hodnoceni, Prispevky.id==Hodnoceni.prispevek_id).filter(Prispevky.id== id).group_by(Prispevky.id, Uzivatele.prezdivka)
            userHodnoceniQuery = postgre.session.query(Hodnoceni.hodnoceni).join(Prispevky).filter(Hodnoceni.uzivatel_id==session["userid"]).filter(Prispevky.id==id).scalar()
            prispevek, komentare, odpovedi, userHodnoceni = prispevekData(komentareQuery, prispevekQuery, userHodnoceniQuery, id)
            print("flask-sqlalchemy")
        # ---> sqlalchemy <--
        else:
            komentareQuery = postgreSQL.execute("SELECT k.id, k.text, u.prezdivka FROM komentare AS k LEFT JOIN uzivatele AS u ON u.id = k.uzivatel_id WHERE k.prispevek_id = '{0}'".format(id)).fetchall()
            prispevekQuery = postgreSQL.execute("SELECT p.id, p.obsah, p.nazev, u.prezdivka, AVG(h.hodnoceni), p.obrazek FROM prispevky AS p LEFT OUTER JOIN uzivatele AS u ON u.id = p.uzivatel_id LEFT JOIN hodnoceni AS h ON h.prispevek_id = p.id WHERE p.id = '{0}' GROUP BY p.id, u.prezdivka".format(id))
            userHodnoceniQuery = postgreSQL.execute("SELECT h.hodnoceni FROM hodnoceni AS h LEFT JOIN uzivatele AS u ON u.id = h.uzivatel_id LEFT JOIN prispevky AS p ON p.id = h.prispevek_id WHERE h.uzivatel_id = '{0}' AND p.id = '{1}'".format(session["userid"], id)).first()
            prispevek, komentare, odpovedi, userHodnoceni = prispevekData(komentareQuery, prispevekQuery, userHodnoceniQuery, id)
            print("sqlalchemy")
        if request.method == "GET":
            return render_template("prispevek.html", session=session, role=role(session), prispevek=prispevek, hodnoceni=hodnoceni, komentare=komentare, odpovedi=odpovedi, userHodnoceni=userHodnoceni)
        if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("prispevek.html", session=session, role=role(session), prispevek=prispevek, hodnoceni=hodnoceni, komentare=komentare, odpovedi=odpovedi, userHodnoceni=userHodnoceni)
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
                # ===> Přidání příspěvku <===
                # ---> flask-sqlalchemy <---
                if flasksqlalchemy:
                    prispevek = Prispevky(
                        nazev = nazev,
                        obsah = obsah,
                        obrazek = obrazek,
                        uzivatel_id = session["userid"]
                    )
                    postgre.session.add(prispevek)
                    postgre.session.commit()
                # ---> sqlalchemy <---
                else:
                    postgreSQL.execute("INSERT INTO prispevky (nazev, obsah, obrazek, uzivatel_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(nazev, obsah, obrazek, session["userid"]))
                return redirect(url_for("forum"))
            return catchall(path)
    else:
        return redirect(url_for("index"))

@flaskApp.route("/forum/roles", methods=["GET", "POST"])
def rolesWeb():
    if session.get("username"):
        if role(session) == "majitel":
            if request.method == "POST":
                if request.form["btn"] == "changerole":
                    changedUser = request.form.get("uzivatelselect")
                    changedRole = request.form.get("roleselect")
                    if flasksqlalchemy:
                        changedUserID = postgre.session.query(Uzivatele.id).filter(Uzivatele.prezdivka==changedUser).scalar()
                        oldRole = postgre.session.query(func.max(Role.id)).join(uzivatele_role).join(Uzivatele).filter(Uzivatele.id==changedUserID).scalar()
                    else:
                        changedUserID = str(postgreSQL.execute("SELECT id FROM uzivatele WHERE prezdivka = '{0}'".format(changedUser)).fetchone()[0])
                        oldRole = str(postgreSQL.execute("SELECT MAX(role_id) FROM uzivatele_role WHERE uzivatel_id = '{0}'".format(changedUserID)).fetchone()[0])
                    if oldRole != "4":
                        if flasksqlalchemy:
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
            if flasksqlalchemy:
                uzivatele = postgre.session.query(Uzivatele.prezdivka, func.string_agg(Role.nazev, aggregate_order_by(literal_column("', '"), Role.id))).select_from(uzivatele_role).join(Role).outerjoin(Uzivatele).group_by(Uzivatele.prezdivka).order_by(Uzivatele.prezdivka).all()
            else:
                uzivatele = postgreSQL.execute("SELECT u.prezdivka, string_agg(r.nazev::character varying, ', ' order by r.id) FROM uzivatele_role AS ur LEFT JOIN uzivatele AS u ON u.id = ur.uzivatel_id LEFT JOIN role AS r ON r.id = ur.role_id GROUP BY u.prezdivka ORDER BY u.prezdivka").fetchall()
            if request.method == "GET":
                return render_template("roles.html",session=session,role=role(session),uzivatele=uzivatele)
            if request.form["btn"] != "logout":
                if request.form["btn"] != "flask":
                    return render_template("roles.html",session=session,role=role(session),uzivatele=uzivatele)
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
                if flasksqlalchemy:
                    if changedEmail != "":
                        if changedEmail not in queryToList(postgre.session.query(Uzivatele.email).all()):
                            email = Uzivatele.query.filter_by(id = session["userid"]).first()
                            email.email = changedEmail
                            postgre.session.commit()
                        else:
                            flash("changeerror")
                    if changedPassword != "":
                        hashed_pass = hashlib.sha256(changedPassword.encode("utf-8")).hexdigest()
                        heslo = Uzivatele.query.filter_by(id = session["userid"]).first()
                        heslo.heslo = hashed_pass
                        postgre.session.commit()
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
                if flasksqlalchemy:
                    deletedRoles = postgre.session.query(Uzivatele).get(session["userid"])
                    deletedRoles.role = []     
                    postgre.session.commit()
                    Hodnoceni.query.filter(Hodnoceni.uzivatel_id == session["userid"]).delete()
                    Odpovedi.query.filter(Odpovedi.uzivatel_id == session["userid"]).delete()
                    Komentare.query.filter(Komentare.uzivatel_id == session["userid"]).delete()
                    Prispevky.query.filter(Prispevky.uzivatel_id == session["userid"]).delete()
                    Uzivatele.query.filter(Uzivatele.id == session["userid"]).delete()
                    postgre.session.commit()
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
        if flasksqlalchemy:
            user = postgre.session.query(Uzivatele.prezdivka, Uzivatele.email, Uzivatele.heslo).filter(Uzivatele.prezdivka==session["username"]).all()[0]
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
