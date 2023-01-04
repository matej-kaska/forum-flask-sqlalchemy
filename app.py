from SQLModels import postgre, Uzivatele, Role, Prispevky, Hodnoceni, Komentare, Odpovedi, uzivatele_role
from SQL import engine, createUser, deleteUser, listUsers, createRole, deleteRole, listRolesOfUser, listRoles, grant, revoke, showGrant, setRole, lockTable, listTables
from flask import Flask, render_template, request, session, flash, redirect, url_for
from sqlalchemy import func
import hashlib

data = []
path = ""
engineUser = "postgres"

flaskApp = Flask(__name__)
flaskApp.app_context().push()
flaskApp.secret_key = "16ecab1875791e2b6ed0c9a6dae5a12a79d92120e1c3afbd3a9c8535ce44660d"
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:123@localhost:5432/forum"

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

postgre.init_app(flaskApp)
postgre.create_all()

def queryToList(query):
    finalList = []
    if query == None or query == "error":
        return "Nemáte dostatečná práva!"
    for data in query:
        for dat in data:
            finalList.append(dat)
    return finalList

def role(session):
    username = session.get("username")
    if username:
        list = postgre.session.query(Role.id).join(Uzivatele, Role.roles).filter(Uzivatele.prezdivka==username).all()
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
    list = postgre.session.query(Hodnoceni.hodnoceni, Uzivatele.prezdivka).join(Uzivatele).filter(Hodnoceni.prispevek_id == id).all()
    for hodnoceni in list:
        prezdivka = hodnoceni[1]
        hodnota = str(hodnoceni[0])
        finalList.append([prezdivka, hodnota])
    for hodnoceni in finalList:
        finalString = finalString + hodnoceni[0] + " - " + hodnoceni[1] + "\u000d"
    return finalString
    
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
            if username not in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars() and email not in postgre.session.execute(postgre.select(Uzivatele.email)).scalars():
                hashed_pass = hashlib.sha256(request.form["password"].encode("utf-8")).hexdigest()
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
                session["username"] = request.form["username"]
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
            prispevek = []
            nextdata = []
            i=0
            rawdata = postgre.session.query(Prispevky.id, Prispevky.obsah, Uzivatele.prezdivka).outerjoin(Uzivatele).all()
            for prispevky in rawdata:
                prispevek = []
                for smalldata in prispevky:
                    prispevek.append(smalldata)
                data.append(prispevek)
            nextdata = postgre.session.query(func.avg(Hodnoceni.hodnoceni)).join(Prispevky).group_by(Prispevky.id).all()
            for item in nextdata:
                item = str(item)[10:13]
                data[i].append(item)
                i = i+1
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
            if username in postgre.session.execute(postgre.select(Uzivatele.prezdivka)).scalars():
                hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()
                if hashed_password == postgre.session.execute(postgre.select(Uzivatele.heslo).where(Uzivatele.prezdivka == username)).scalar():
                    session["username"] = request.form["username"]
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
    return render_template("index.html", session=session, role=role(session))

@flaskApp.route("/forum/<id>", methods=["GET"])
def prispevek(id):
    if session.get("username"):
        if request.method == "GET":
            prispevek = []
            komentare = []
            odpovedi = []
            obrazky = []
            komentareIDs = []
            rawOdpovedi = []
            for pris in data:
                if str(pris[0]) == id:
                    prispevek = pris
            hodnoceni = hodnoceniList(id)
            rawKomentare = postgre.session.query(Komentare.id, Komentare.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Komentare.prispevek_id==id).all()
            for komentar in rawKomentare:
                comm = []
                for koment in komentar:
                    comm.append(koment)
                komentareIDs.append(comm[0])
                komentare.append(comm)
            for odpoved in komentareIDs:
                rawOdpovedi.append(postgre.session.query(Odpovedi.komentar_id, Odpovedi.text, Uzivatele.prezdivka).outerjoin(Uzivatele).filter(Odpovedi.komentar_id==odpoved).all())
            for rawOdpoved in rawOdpovedi:
                for odpoved in rawOdpoved:
                    odpo = []
                    for reply in odpoved:
                        odpo.append(reply)
                    odpovedi.append(odpo)
            rawObrazky = postgre.session.query(Prispevky.obrazek).filter(Prispevky.id==id).all()
            for obrazek in rawObrazky:
                for obraz in obrazek:
                    obrazky.append(obraz)
            return render_template("prispevek.html", session=session, role=role(session), prispevek=prispevek, hodnoceni=hodnoceni, komentare=komentare, odpovedi=odpovedi, obrazky=obrazky)
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
                return render_template("sql.html", session=session, role=role(session), users=finalusers, uzivatele=uzivatele, roles=roles, rolesofuser=rolesofuser, roleuser=session["roleuser"], privofuser=privofuser, privuser=session["privuser"], selectedtabulka=session["selectedtabulka"], tabulky=tabulky, tabulkydata=tabulkydata, engineUser=session["engineUser"])
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

if __name__ == "__main__":
    flaskApp.run(debug=True, host="0.0.0.0")
