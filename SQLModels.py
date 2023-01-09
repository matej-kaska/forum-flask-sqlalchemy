from flask_sqlalchemy import SQLAlchemy

postgre = SQLAlchemy()

uzivatele_role = postgre.Table('uzivatele_role',
    postgre.Column('role_id', postgre.Integer, postgre.ForeignKey('role.id'), primary_key=True),
    postgre.Column('uzivatel_id', postgre.Integer, postgre.ForeignKey('uzivatele.id'), primary_key=True))

class Uzivatele(postgre.Model):
    __tablename__ = 'uzivatele'
    id = postgre.Column(postgre.Integer, postgre.Sequence("users_id_seq", start=1), primary_key=True, nullable=False)
    prezdivka = postgre.Column(postgre.String, nullable=False)
    heslo = postgre.Column(postgre.String, nullable=False)
    email = postgre.Column(postgre.String, nullable=False)
    role = postgre.relationship('Role', secondary=uzivatele_role, backref="uzivatel_role")

class Role(postgre.Model):
    __tablename__ = 'role'
    id = postgre.Column(postgre.Integer, primary_key=True)
    nazev = postgre.Column(postgre.String, nullable=False)

class Komentare(postgre.Model):
    __tablename__ = 'komentare'
    id = postgre.Column(postgre.Integer, postgre.Sequence("komentare_id_seq", start=1), primary_key=True)
    text = postgre.Column(postgre.String, nullable=False)
    uzivatel_id = postgre.Column(postgre.Integer, postgre.ForeignKey("uzivatele.id"), nullable=False)
    prispevek_id = postgre.Column(postgre.Integer, postgre.ForeignKey("prispevky.id"), nullable=False)

class Prispevky(postgre.Model):
    __tablename__ = 'prispevky'
    id = postgre.Column(postgre.Integer, postgre.Sequence("posts_id_seq", start=1), primary_key=True)
    nazev = postgre.Column(postgre.String, nullable=False)
    obsah = postgre.Column(postgre.String, nullable=False)
    obrazek = postgre.Column(postgre.String, nullable=False)
    uzivatel_id = postgre.Column(postgre.Integer, postgre.ForeignKey("uzivatele.id"), nullable=False)

class Odpovedi(postgre.Model):
    __tablename__ = 'odpovedi'
    id = postgre.Column(postgre.Integer, postgre.Sequence("odpovedi_id_seq", start=1), primary_key=True)
    text = postgre.Column(postgre.String, nullable=False)
    uzivatel_id = postgre.Column(postgre.Integer, postgre.ForeignKey("uzivatele.id"), nullable=False)
    komentar_id = postgre.Column(postgre.Integer, postgre.ForeignKey("komentare.id"), nullable=False)

class Hodnoceni(postgre.Model):
    __tablename__ = 'hodnoceni'
    id = postgre.Column(postgre.Integer, postgre.Sequence("hodnoceni_id_seq", start=1), primary_key=True)
    hodnoceni = postgre.Column(postgre.Integer, nullable=False)
    uzivatel_id = postgre.Column(postgre.Integer, postgre.ForeignKey("uzivatele.id"), nullable=False)
    prispevek_id = postgre.Column(postgre.Integer, postgre.ForeignKey("prispevky.id"), nullable=False)

class Uzivatele_audits(postgre.Model):
    __tablename__ = 'uzivatele_audits'
    id = postgre.Column(postgre.Integer, primary_key=True)
    uzivatel_id = postgre.Column(postgre.Integer, nullable=False)
    prezdivka = postgre.Column(postgre.String, nullable=False)
    heslo = postgre.Column(postgre.String, nullable=False)
    email = postgre.Column(postgre.String, nullable=False)
    zmena = postgre.Column(postgre.DateTime, nullable=False)