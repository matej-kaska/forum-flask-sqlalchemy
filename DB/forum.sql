PGDMP         4                 {            forum    14.3    14.3 T    M           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            N           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            O           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            P           1262    16394    forum    DATABASE     a   CREATE DATABASE forum WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'Czech_Czechia.1250';
    DROP DATABASE forum;
                postgres    false            �            1255    32869    count_comm(integer)    FUNCTION       CREATE FUNCTION public.count_comm(komentar integer) RETURNS integer
    LANGUAGE plpgsql
    AS $$DECLARE celkem integer;

BEGIN

	SELECT COUNT(k.id) INTO celkem
	FROM komentare k
	JOIN prispevky p
	ON p.id = k.prispevek_id
	WHERE k.prispevek_id = komentar;
	
	RETURN celkem;
	
END;
$$;
 3   DROP FUNCTION public.count_comm(komentar integer);
       public          postgres    false            �            1255    32842    count_rows_of_table(text, text)    FUNCTION     �  CREATE FUNCTION public.count_rows_of_table(schema text, tablename text) RETURNS integer
    LANGUAGE plpgsql
    AS $$DECLARE
  query_template CONSTANT TEXT NOT NULL :='SELECT COUNT(*) FROM "?schema"."?tablename"';

  query CONSTANT TEXT NOT NULL :=
    REPLACE(
      REPLACE(
        query_template, '?schema', schema),
     '?tablename', tablename);

  result INT NOT NULL := -1;
BEGIN
  EXECUTE query INTO result;
  RETURN result;
END;$$;
 G   DROP FUNCTION public.count_rows_of_table(schema text, tablename text);
       public          postgres    false            �            1255    32871    random_hodnoceni()    FUNCTION     ~  CREATE FUNCTION public.random_hodnoceni() RETURNS void
    LANGUAGE plpgsql
    AS $$DECLARE 
	cur CURSOR FOR SELECT id, hodnoceni, uzivatel_id, prispevek_id FROM hodnoceni;
	cur_row RECORD;
BEGIN
	open cur;
LOOP
	fetch cur into cur_row;
	EXIT WHEN NOT FOUND;
	UPDATE hodnoceni SET hodnoceni = trunc(random() * 5 + 1) WHERE cur_row.id = hodnoceni.id;
END LOOP;
	close cur;
END;
$$;
 )   DROP FUNCTION public.random_hodnoceni();
       public          postgres    false            �            1255    32885    random_random_hodnoceni() 	   PROCEDURE       CREATE PROCEDURE public.random_random_hodnoceni()
    LANGUAGE plpgsql
    AS $$DECLARE 
	cur CURSOR FOR SELECT id, hodnoceni, uzivatel_id, prispevek_id FROM hodnoceni;
	cur_row RECORD;
BEGIN
	open cur;
LOOP
	fetch cur into cur_row;
	EXIT WHEN NOT FOUND;
	UPDATE hodnoceni SET hodnoceni = trunc(random() * 5 + 1) WHERE cur_row.id = hodnoceni.id;
END LOOP;
	close cur;
IF trunc(random() * 2 + 1) = 1 THEN
    COMMIT;
	RAISE NOTICE 'Commitnuto! (Success)';
ELSE
	ROLLBACK;
	raise NOTICE 'Rollbacknuto! (Fail)';
END IF;
END;
$$;
 1   DROP PROCEDURE public.random_random_hodnoceni();
       public          postgres    false            �            1255    32882    uzivatele_changes()    FUNCTION     `  CREATE FUNCTION public.uzivatele_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	IF NEW.prezdivka <> OLD.prezdivka OR NEW.heslo <> OLD.heslo OR NEW.email <> OLD.email THEN
		 INSERT INTO uzivatele_audits(uzivatel_id,prezdivka,heslo,email,zmena)
		 VALUES(OLD.id,OLD.prezdivka,OLD.heslo,OLD.email,now());
	END IF;

	RETURN NEW;
END;
$$;
 *   DROP FUNCTION public.uzivatele_changes();
       public          postgres    false            �            1259    16395 	   hodnoceni    TABLE     �   CREATE TABLE public.hodnoceni (
    id integer NOT NULL,
    hodnoceni numeric NOT NULL,
    uzivatel_id integer NOT NULL,
    prispevek_id integer NOT NULL
);
    DROP TABLE public.hodnoceni;
       public         heap    postgres    false            Q           0    0    TABLE hodnoceni    ACL     2   GRANT DELETE ON TABLE public.hodnoceni TO matejr;
          public          postgres    false    209            �            1259    16400    hodnoceni_id_seq    SEQUENCE     �   CREATE SEQUENCE public.hodnoceni_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.hodnoceni_id_seq;
       public          postgres    false    209            R           0    0    hodnoceni_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.hodnoceni_id_seq OWNED BY public.hodnoceni.id;
          public          postgres    false    210            �            1259    16401 	   komentare    TABLE     �   CREATE TABLE public.komentare (
    id integer NOT NULL,
    uzivatel_id integer NOT NULL,
    prispevek_id integer NOT NULL,
    text text NOT NULL
);
    DROP TABLE public.komentare;
       public         heap    postgres    false            S           0    0    TABLE komentare    ACL     2   GRANT DELETE ON TABLE public.komentare TO matejr;
          public          postgres    false    211            �            1259    16406    komentare_id_seq    SEQUENCE     �   CREATE SEQUENCE public.komentare_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 '   DROP SEQUENCE public.komentare_id_seq;
       public          postgres    false    211            T           0    0    komentare_id_seq    SEQUENCE OWNED BY     E   ALTER SEQUENCE public.komentare_id_seq OWNED BY public.komentare.id;
          public          postgres    false    212            �            1259    16419    role    TABLE     \   CREATE TABLE public.role (
    id integer NOT NULL,
    nazev character varying NOT NULL
);
    DROP TABLE public.role;
       public         heap    postgres    false            U           0    0 
   TABLE role    ACL     -   GRANT DELETE ON TABLE public.role TO matejr;
          public          postgres    false    217            �            1259    16431    uzivatele_role    TABLE     g   CREATE TABLE public.uzivatele_role (
    role_id integer NOT NULL,
    uzivatel_id integer NOT NULL
);
 "   DROP TABLE public.uzivatele_role;
       public         heap    postgres    false            V           0    0    TABLE uzivatele_role    ACL     7   GRANT DELETE ON TABLE public.uzivatele_role TO matejr;
          public          postgres    false    221            �            1259    24695    number_of_sers    VIEW     �   CREATE VIEW public.number_of_sers AS
 SELECT r.nazev
   FROM (public.role r
     RIGHT JOIN public.uzivatele_role ur ON ((r.id = ur.role_id)));
 !   DROP VIEW public.number_of_sers;
       public          postgres    false    221    217    217            W           0    0    TABLE number_of_sers    ACL     7   GRANT DELETE ON TABLE public.number_of_sers TO matejr;
          public          postgres    false    222            �            1259    16413 	   prispevky    TABLE     �   CREATE TABLE public.prispevky (
    id integer NOT NULL,
    nazev character varying NOT NULL,
    obsah text NOT NULL,
    obrazek character varying NOT NULL,
    uzivatel_id integer NOT NULL
);
    DROP TABLE public.prispevky;
       public         heap    postgres    false            X           0    0    TABLE prispevky    ACL     2   GRANT DELETE ON TABLE public.prispevky TO matejr;
          public          postgres    false    215            �            1259    16425 	   uzivatele    TABLE     �   CREATE TABLE public.uzivatele (
    id integer NOT NULL,
    prezdivka character varying NOT NULL,
    heslo character varying NOT NULL,
    email character varying NOT NULL
);
    DROP TABLE public.uzivatele;
       public         heap    postgres    false            Y           0    0    TABLE uzivatele    ACL     2   GRANT DELETE ON TABLE public.uzivatele TO matejr;
          public          postgres    false    219            �            1259    32849    number_of_users    VIEW     �  CREATE VIEW public.number_of_users AS
 SELECT r.nazev,
    count(r.nazev) AS pocet_uzivatelu,
    count(p.id) AS pocet_prispevku
   FROM (((public.role r
     RIGHT JOIN public.uzivatele_role ur ON ((r.id = ur.role_id)))
     JOIN public.uzivatele u ON ((u.id = ur.uzivatel_id)))
     LEFT JOIN public.prispevky p ON ((p.uzivatel_id = u.id)))
  GROUP BY r.nazev
  ORDER BY (count(r.nazev));
 "   DROP VIEW public.number_of_users;
       public          postgres    false    221    215    215    217    217    219    221            �            1259    16407    odpovedi    TABLE     �   CREATE TABLE public.odpovedi (
    id integer NOT NULL,
    text text NOT NULL,
    uzivatel_id integer NOT NULL,
    komentar_id integer NOT NULL
);
    DROP TABLE public.odpovedi;
       public         heap    postgres    false            Z           0    0    TABLE odpovedi    ACL     1   GRANT DELETE ON TABLE public.odpovedi TO matejr;
          public          postgres    false    213            �            1259    16412    odpovedi_id_seq    SEQUENCE     �   CREATE SEQUENCE public.odpovedi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public.odpovedi_id_seq;
       public          postgres    false    213            [           0    0    odpovedi_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public.odpovedi_id_seq OWNED BY public.odpovedi.id;
          public          postgres    false    214            �            1259    16418    posts_id_seq    SEQUENCE     �   CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.posts_id_seq;
       public          postgres    false    215            \           0    0    posts_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.posts_id_seq OWNED BY public.prispevky.id;
          public          postgres    false    216            �            1259    16424    roles_id_seq    SEQUENCE     �   CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.roles_id_seq;
       public          postgres    false    217            ]           0    0    roles_id_seq    SEQUENCE OWNED BY     <   ALTER SEQUENCE public.roles_id_seq OWNED BY public.role.id;
          public          postgres    false    218            �            1259    16430    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          postgres    false    219            ^           0    0    users_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.users_id_seq OWNED BY public.uzivatele.id;
          public          postgres    false    220            �            1259    32877    uzivatele_audits    TABLE       CREATE TABLE public.uzivatele_audits (
    id integer NOT NULL,
    uzivatel_id integer NOT NULL,
    prezdivka character varying NOT NULL,
    heslo character varying NOT NULL,
    email character varying NOT NULL,
    zmena timestamp(6) without time zone NOT NULL
);
 $   DROP TABLE public.uzivatele_audits;
       public         heap    postgres    false            �            1259    32876    uzivatele_audits_id_seq    SEQUENCE     �   ALTER TABLE public.uzivatele_audits ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.uzivatele_audits_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          postgres    false    225            �           2604    24576    hodnoceni id    DEFAULT     l   ALTER TABLE ONLY public.hodnoceni ALTER COLUMN id SET DEFAULT nextval('public.hodnoceni_id_seq'::regclass);
 ;   ALTER TABLE public.hodnoceni ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    210    209            �           2604    24577    komentare id    DEFAULT     l   ALTER TABLE ONLY public.komentare ALTER COLUMN id SET DEFAULT nextval('public.komentare_id_seq'::regclass);
 ;   ALTER TABLE public.komentare ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    212    211            �           2604    24578    odpovedi id    DEFAULT     j   ALTER TABLE ONLY public.odpovedi ALTER COLUMN id SET DEFAULT nextval('public.odpovedi_id_seq'::regclass);
 :   ALTER TABLE public.odpovedi ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    214    213            �           2604    24579    prispevky id    DEFAULT     h   ALTER TABLE ONLY public.prispevky ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);
 ;   ALTER TABLE public.prispevky ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    216    215            �           2604    24580    role id    DEFAULT     c   ALTER TABLE ONLY public.role ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);
 6   ALTER TABLE public.role ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    218    217            �           2604    24581    uzivatele id    DEFAULT     h   ALTER TABLE ONLY public.uzivatele ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 ;   ALTER TABLE public.uzivatele ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    220    219            <          0    16395 	   hodnoceni 
   TABLE DATA           M   COPY public.hodnoceni (id, hodnoceni, uzivatel_id, prispevek_id) FROM stdin;
    public          postgres    false    209   1a       >          0    16401 	   komentare 
   TABLE DATA           H   COPY public.komentare (id, uzivatel_id, prispevek_id, text) FROM stdin;
    public          postgres    false    211   `c       @          0    16407    odpovedi 
   TABLE DATA           F   COPY public.odpovedi (id, text, uzivatel_id, komentar_id) FROM stdin;
    public          postgres    false    213   �i       B          0    16413 	   prispevky 
   TABLE DATA           K   COPY public.prispevky (id, nazev, obsah, obrazek, uzivatel_id) FROM stdin;
    public          postgres    false    215   m       D          0    16419    role 
   TABLE DATA           )   COPY public.role (id, nazev) FROM stdin;
    public          postgres    false    217   �       F          0    16425 	   uzivatele 
   TABLE DATA           @   COPY public.uzivatele (id, prezdivka, heslo, email) FROM stdin;
    public          postgres    false    219   K�       J          0    32877    uzivatele_audits 
   TABLE DATA           [   COPY public.uzivatele_audits (id, uzivatel_id, prezdivka, heslo, email, zmena) FROM stdin;
    public          postgres    false    225   ��       H          0    16431    uzivatele_role 
   TABLE DATA           >   COPY public.uzivatele_role (role_id, uzivatel_id) FROM stdin;
    public          postgres    false    221   Q�       _           0    0    hodnoceni_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.hodnoceni_id_seq', 1, false);
          public          postgres    false    210            `           0    0    komentare_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.komentare_id_seq', 1, false);
          public          postgres    false    212            a           0    0    odpovedi_id_seq    SEQUENCE SET     =   SELECT pg_catalog.setval('public.odpovedi_id_seq', 1, true);
          public          postgres    false    214            b           0    0    posts_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.posts_id_seq', 15, true);
          public          postgres    false    216            c           0    0    roles_id_seq    SEQUENCE SET     :   SELECT pg_catalog.setval('public.roles_id_seq', 4, true);
          public          postgres    false    218            d           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 29, true);
          public          postgres    false    220            e           0    0    uzivatele_audits_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.uzivatele_audits_id_seq', 2, true);
          public          postgres    false    224            �           2606    16441    hodnoceni hodnoceni_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.hodnoceni
    ADD CONSTRAINT hodnoceni_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.hodnoceni DROP CONSTRAINT hodnoceni_pkey;
       public            postgres    false    209            �           2606    16443    komentare komentare_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.komentare
    ADD CONSTRAINT komentare_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.komentare DROP CONSTRAINT komentare_pkey;
       public            postgres    false    211            �           2606    16445    odpovedi odpovedi_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.odpovedi
    ADD CONSTRAINT odpovedi_pkey PRIMARY KEY (id);
 @   ALTER TABLE ONLY public.odpovedi DROP CONSTRAINT odpovedi_pkey;
       public            postgres    false    213            �           2606    16447    prispevky prispevky_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.prispevky
    ADD CONSTRAINT prispevky_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.prispevky DROP CONSTRAINT prispevky_pkey;
       public            postgres    false    215            �           2606    16449    role role_pkey 
   CONSTRAINT     L   ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pkey PRIMARY KEY (id);
 8   ALTER TABLE ONLY public.role DROP CONSTRAINT role_pkey;
       public            postgres    false    217            �           2606    16451    uzivatele uzivatele_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.uzivatele
    ADD CONSTRAINT uzivatele_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.uzivatele DROP CONSTRAINT uzivatele_pkey;
       public            postgres    false    219            �           2606    16503 "   uzivatele_role uzivatele_role_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public.uzivatele_role
    ADD CONSTRAINT uzivatele_role_pkey PRIMARY KEY (role_id, uzivatel_id);
 L   ALTER TABLE ONLY public.uzivatele_role DROP CONSTRAINT uzivatele_role_pkey;
       public            postgres    false    221    221            �           1259    16452    fki_komentare_fkey    INDEX     N   CREATE INDEX fki_komentare_fkey ON public.odpovedi USING btree (komentar_id);
 &   DROP INDEX public.fki_komentare_fkey;
       public            postgres    false    213            �           1259    16453    fki_prispevky_fkey    INDEX     P   CREATE INDEX fki_prispevky_fkey ON public.komentare USING btree (prispevek_id);
 &   DROP INDEX public.fki_prispevky_fkey;
       public            postgres    false    211            �           1259    16454    fki_roles_fkey    INDEX     L   CREATE INDEX fki_roles_fkey ON public.uzivatele_role USING btree (role_id);
 "   DROP INDEX public.fki_roles_fkey;
       public            postgres    false    221            �           1259    16455    fki_users_fkey    INDEX     P   CREATE INDEX fki_users_fkey ON public.uzivatele_role USING btree (uzivatel_id);
 "   DROP INDEX public.fki_users_fkey;
       public            postgres    false    221            �           1259    16456    fki_uzivatele_fkey    INDEX     O   CREATE INDEX fki_uzivatele_fkey ON public.komentare USING btree (uzivatel_id);
 &   DROP INDEX public.fki_uzivatele_fkey;
       public            postgres    false    211            �           1259    32867    idx_prispevky    INDEX     K   CREATE UNIQUE INDEX idx_prispevky ON public.prispevky USING btree (obsah);
 !   DROP INDEX public.idx_prispevky;
       public            postgres    false    215            �           2620    32883    uzivatele uzivatele_change    TRIGGER     |   CREATE TRIGGER uzivatele_change BEFORE UPDATE ON public.uzivatele FOR EACH ROW EXECUTE FUNCTION public.uzivatele_changes();
 3   DROP TRIGGER uzivatele_change ON public.uzivatele;
       public          postgres    false    219    239            �           2606    16457    odpovedi komentare_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.odpovedi
    ADD CONSTRAINT komentare_fkey FOREIGN KEY (komentar_id) REFERENCES public.komentare(id);
 A   ALTER TABLE ONLY public.odpovedi DROP CONSTRAINT komentare_fkey;
       public          postgres    false    211    3222    213            �           2606    16462    komentare prispevky_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.komentare
    ADD CONSTRAINT prispevky_fkey FOREIGN KEY (prispevek_id) REFERENCES public.prispevky(id);
 B   ALTER TABLE ONLY public.komentare DROP CONSTRAINT prispevky_fkey;
       public          postgres    false    3228    215    211            �           2606    16467    hodnoceni prispevky_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.hodnoceni
    ADD CONSTRAINT prispevky_fkey FOREIGN KEY (prispevek_id) REFERENCES public.prispevky(id);
 B   ALTER TABLE ONLY public.hodnoceni DROP CONSTRAINT prispevky_fkey;
       public          postgres    false    215    209    3228            �           2606    16472    uzivatele_role role_fkey    FK CONSTRAINT     v   ALTER TABLE ONLY public.uzivatele_role
    ADD CONSTRAINT role_fkey FOREIGN KEY (role_id) REFERENCES public.role(id);
 B   ALTER TABLE ONLY public.uzivatele_role DROP CONSTRAINT role_fkey;
       public          postgres    false    3230    217    221            �           2606    16477    uzivatele_role uzivatele_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.uzivatele_role
    ADD CONSTRAINT uzivatele_fkey FOREIGN KEY (uzivatel_id) REFERENCES public.uzivatele(id);
 G   ALTER TABLE ONLY public.uzivatele_role DROP CONSTRAINT uzivatele_fkey;
       public          postgres    false    219    3232    221            �           2606    16482    prispevky uzivatele_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.prispevky
    ADD CONSTRAINT uzivatele_fkey FOREIGN KEY (uzivatel_id) REFERENCES public.uzivatele(id);
 B   ALTER TABLE ONLY public.prispevky DROP CONSTRAINT uzivatele_fkey;
       public          postgres    false    3232    219    215            �           2606    16487    komentare uzivatele_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.komentare
    ADD CONSTRAINT uzivatele_fkey FOREIGN KEY (uzivatel_id) REFERENCES public.uzivatele(id);
 B   ALTER TABLE ONLY public.komentare DROP CONSTRAINT uzivatele_fkey;
       public          postgres    false    3232    219    211            �           2606    16492    odpovedi uzivatele_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.odpovedi
    ADD CONSTRAINT uzivatele_fkey FOREIGN KEY (uzivatel_id) REFERENCES public.uzivatele(id);
 A   ALTER TABLE ONLY public.odpovedi DROP CONSTRAINT uzivatele_fkey;
       public          postgres    false    213    3232    219            �           2606    16497    hodnoceni uzivatele_fkey    FK CONSTRAINT        ALTER TABLE ONLY public.hodnoceni
    ADD CONSTRAINT uzivatele_fkey FOREIGN KEY (uzivatel_id) REFERENCES public.uzivatele(id);
 B   ALTER TABLE ONLY public.hodnoceni DROP CONSTRAINT uzivatele_fkey;
       public          postgres    false    209    219    3232            <     x�5�۱�0E�oQ���{I�uܳOf�;��|=m6�/���o��n��Nr�;���f�q�5w��]�{_�����<m4?�wp)�� q}	F��=r"<���<Z�pu那?���w�,]J; �;ȥ��k��h�E~vѵ);�&���Z�Թ��T��p�i�6�zA��]�;S^�$<Y�L���ö:�.(pvAXʰ�l���@�8}����VuA�.H�X]�j+�
T]��2%���;Gw�
���BΡ���3(d��l�^�� ��Bn�P�8mT�ҥ���ʗ6ڨʗ������oG5�-R�ê�).��,_���	F���,_��U~7#ʗh�ޤz����#��D"�ޤ�A)6�Qu߭f�r�rr�rpܢ��d[�节ߔ�bC���C�n��K4t9W����`�k�����5g1�\����#
��TX5Af�'s�᷵��;�h���7]��j�5>�:��Q��G�S�� �����}���IΝ�$�N֩�T�,m$Y���������      >   U  x�eV�n�8��_1q� �׎����p�"�!q�)�k(��R�HA�������+W�0R\�n��_��Z�.lS��͛7oxx����ä��Oו�\�U�z�vIu�6��m�f*'lP�t��t��
I'����7�uH�'���eO��
����_��s�x|�:eS��\�NK�� �Y�v��Rlo�4�lZD�ns������Zj;��4n�%moy��T���P52��n����^��\A�Ő� a{�:��=NV�du����Q�i�h�E�Aw�����%��.Il��B1�nR�6Jb3bwF��,V�"mG�[!���«��&)�����K�<��5!�ʭ�Z�~{KA���<0K���BN_��Y �H�ĒU)���k���V*�.O�Co��m��/p�Y������E

eQ9��t��� ����$Yc��J�!�Nj�2%�e���F�F)�T���a�l%C�%���n�c�C�^� 9�L_�6Z�RG֢4��REuI�Z,#M�3���ֱ�;�����!>s�t�nJ\�7�i�~���w-��Oӗ&�� -��/+b�y�A� )uKR3k{H��kJ�OP a��:>8���L���p�b��SףK*.' �.�JH��N7ɍ��T�e��ڡ5A�Hq-�bnm6��?h���Z�0z�����J�H�+��ub([Z��6�B���J��Be=�ԣk�u�A���Vɫ�B�W�U"�d� �Fy N�`��	�I�ٺ�Mʈ:Q I����+]�x�d,T�ho��_ �cn�C`���
/��D�u��ר�sUd�9c� ��Ú�)�w�IDTU{�h�v�m�{L�^i��G�l	{�}<Л�b�#`��:�MN֮C����FU��C'HH$$(sk�ap���~n������Qr�Ģ�FS`��Α!d�'e|Y����}8���5
+�ճ� �id3��e�ų��e�71����C�����겏z׆>�"ꋯ�ݥq�Z���	��09�_o.ٰ�;�GHRZ�鶄]ߠ�9jٰ� c�*m�J�,ԣ�%���*ec�IC�����8����!��e��5��$l��j^�ih������S� p�q�*�ř}4ZQ�$T�#�K�\����%�ɤ`�}T��¸�-;� �Go 5x >���ӆ�����	Ak(��47�B�O]����=�1�����E��䢄�&V�;SH�;SÐQ��v^G|���9u@��lq�=t��z ����`)��;>O��S�iq������J^#�뜌���^�� �R�k�a~lIl�:���]��.+���_q��h�8&'OᏟ\(��I��w��<6D�VmP�z���$��,P8�}4���^���xܷ�Q��0:V[&+�se�3*��HA�ڨ �>%�!�<��Y5.3�[�ӷ��Y��KS�#�F�8X12@BH�G㐮�H��<4�% �&����5F��s��!: �/��;��.�xc�CM�95T0Wս���y����?�`�û��:��h*0(�y�
�]���lĖ����gϏ����m��a�x���t�{�X,�%M$T      @   G  x�mT;n�F���((��Ь���LJl,`��'�a��I6���<�`�h
��h��W���H�fuի��͙�V�.ϏT��Y7��&�����0�AGs���SI?kj�1�=���eݻO)��wi�/�u�2�����t}|h��O
L�f�=S��2f>teY�u^ܨ_u6!b������D�'cSI�4�6��:�Ķ�z���hv;��o��[\�n:eW'j�1<t߶������ǉ4��\1�@]g�,B��hX��Y�ݠ�R]���Z��h'�p��kK����`%
؞m
&о�Ch�=y��Pc��,��J���n]eU	`Z=գM�K-5�%�y]��R�Q�ŕ�Ξ���z��z\>�=���L��q~ZPg&�(;��o���Z�_+O���|�4�C� E���P�ڗ�@�]���R�-��d��Vw�U>޳�/�B��ɻ�q���)��1q�2�翆�?>EX� ��N\m�}:u!%X���D��eH�:n�J���ϏQ��Y�ڭ����<�׎�g�4��P��Un� ���!�����p��-����4�WZ����b�ͅ�..���Hk�>ޯƈڊPZ�8���S�suS����XòK�>�q�Zq=�Rx��W�@����:�k�a�N�5��=��,5,.�\o�-e�\svFP��� ����g݂�7�^>"�fHM��2y�����wt[�����
΃�j���4�����ё��L�ՋC�Sh��ɓ�y[l�$�C�~�����&���XLz�wìX����=�F�*V^>5���U6k&�B��9/~+���S�      B      x�}ZM�Ǒ=���� �b��3$e��eawM��(-@�������BUV�]'}0���v��/{0����/��"�z��baY��̌�x�"��/���V��ftf��]�������D[�1���.+ה��<���}]ezg�`��7f���Bn+�vc�}�\�v��+L�rWm�jӅ��Ks��8v�a�ƙa��l��T�f���Ӑm�j7&�𛯬�oM���yX�}��cc+gZ[bM��>�$�h�,n��>,�C�� i�Wz꺯���P�&��\y�<�%'�c�Tn�±�}��X�+6k�4�+g�!*��H�+|�v�'f
�dp�bi��]�#j������e7�Ї��[��恚ç����ؔ�u���}W�R�Ǐ�oh���UI��!��@pl`�b�K�h�{�u��*BIW�k�g�SIǦ�1fP������_����ys��8�=���P7P�K��^'�P�%�!A�O���/k�g6�8�B���#Ö�+�����C�i����[����j�,*�	���v �-7r>�=�@sV�r�v�}3�r��r5� �a�U�P�	s�u�ocgwD,Ι��{_ ��8����:�L�"HLt�b��_�-d�P��<qf�=�V,Ec��Òj{ٗ����l�Q?O\�ʽIx���5���<=��S�C3�ޫ'�ю>&�g2�h�V��xDe��"��d�j�/P�[U���T;� ^p���k
��^g�~�~�J�6P��Jp
(B%�c:�R�W@L�/��́-ֈ^��j�\<����G�ǖV��;J7��.��6t��6֮�e��8:7'zM.z���V~ A�ў��=���.04��w��]�i-:*�tL΄����L4���
��d�-:C�Ҽ�HQ��Q���k\ ��o;��Z�=n��9�!~ z�c�<�~�\��1Pa��<�`�CL��/Ͼ��	�����:���'��0�Kd��҅J�j�x��腐���s,�P�Z.+QEC7>�<��W��_t���2GpZi6���V=���j@a�Xy�G�	�cUj�D��_��:���&����[o�0�E�����ٚlC��h��< ��`b�j	���/}W3=
XB�B`�$��ߙ�8s6@�~V�� ,=7�#BQi���V�'��	�w�n/`�r�`�Q�p��*�5����8�&�5<�e�#:�qD��14gH�P����4+��c	0[���� �T�Xt*�|�e�h�!���E��&��1t��	Кף+����oLnK,)r�V�V�/���q�x/z�Ǘ�<���O����(G���!ܿ��C)�jl�{p���e�Q��} ��74��U|���{�5
l��������@]�&;B��wm �`�G.��G3�6���8$ǁ�$�3.�C�(�SbXd�2��H���"��_ꡏN#:"j������1�yA媓���	"�	2l�Y0S�s��`�@-)���
��ȶ�$x�u#7*\�?h����n�]z��~XU�<b&BN��)8Q��������%K5�/�
\��^-�����w�8B��z��(%�B�-� v�
�����kȇ�oִol��e��Y<�ݿ���2�}�3��|D3H$v#BBfco�>����D�d�n/�r�8HR��J�]`y8�ML�CDz�?@��z����X�ʄ���`���
{�������U���-�;�&g�Z����&O�W�وkE��:�@0^�M�x�'�~��k�dCW����Y�����}.�g3��,Zc}��<4�����E����)��4���`�f �5v愈B�S�Ł�Hxp>�
�Ŗ�6��09QG��9U�Ŀ��0߄�<��3�I9D|���:i�
[!Z��#����d�KP|$��G��qw�"9��'��*ƶ�z:�U���G_���.C������5�wN��߮:W���/���o��-�������EVe�p��k�Rm�=K�"��~�
�k��v���D}�wT*ِ3��d�U��0��,B��K�1�� z���z{����f�7WVJB���gu3��+�<-�����%bX1�	k�R��}�w �v�k�sk8�#�9X�;U��S�EG�?��	����o�������2nA��Z�XEt��-�_�j�8�u��ŗ�PZ�,�Q�6�D����1�BHC�a�*�g�]�p)�$+�
d�J�Uz]ق$��H�\��jY��7u��LR�I���;��+j��pج�(4��$bY���VuE�l�8�h�ƣ�Y` cQKi*�$A�YX��F1�2dV��2�@�X�>�~c妢�A!��rD*fE��`C��Gl��rEf���q����B��dy/\��/��Ō���mX@����(2��-ӗ(X�fa��Ɯ��,���#��gă@CG�L����iQ�ְ��]�W��I�M��4���߬�'w�+�+��x��Gw�`u2�3\o^"m�
;��ݟi&��\ �TڔL�t�0�-�Ћ�(H���%`�y�H�A��Ŏ$�۫Z ����O�
�i���Sۀ��ݪaI�Җ1)�b6�^u�|:�/7���O�������ӧ_��>�����g�\�[�ɳ�/���	���-�7�i�,���!���Z�Z����7u��i��=q��[�]�����^س<�����Ay��N|
|u>t�\�_��S�-�����4/,�~�Y5��ݑ.��U�.�6�t�;�^5��b|&�|�/�-2�k�2��t�ۂm���'�M��f0#�� ����͚\�u��L/���5�c5$����O/R��sto��������O�~�|����r,{/�G�Y��ej �����zoW�C�j�r�L!Ur��M2�;��+]IؔMj��Nc��.%]�nb}[[5�,`�����`�c���&�2V�B�҄���G�Ψ@�����C.��;�:��P	o:̣���]�Z�.9#к`�bdP�~/���	�4��%R&L����B�I��=V>-�.�!؜�p%6�`�jk�s�G@��5/�5)RWa6�&�_*��N���-]a A��Xa-m@�a"��O�Š	0�H�5(�o�C����pڒb�L<�K}���O�Ώ�n-�Θ��~�X3�H�Հ���T�]-�u�I#ƾ%���
��H��e��늗)m����jyYhGkju?���qY��#fa�E����+����ٽ/>??�{���S��'c5�d�Np�p��J5?�'�-O�Q�7����Ư�	��m9�L�c/������������]��J�^<�~P���K�:sG܌,��,�T�d����`�~�}�I!E�6�ᡡ�׆�����������֛ܳ�EtVl>��c�' �5��6�A�A��C$�����``����� ];�G:�K+L�y �)à'��;�҈^�y���F~^{֮؃s�	�s�-�ҹ��%]�(��>�0���i��f_cq��e;$C�Ti�����
bU#Qm�^R
��r+8��8�(��,m�␰@Pr��� �ۨ�D�:N��7�ll�����D��~/�fy�*5�R�����\9��Fl,�㈺S�etPi_�7�S�X�4#E��ÿ@LR�
�K��Dģi�̃�77�{6��L:���,�>|[%�}�a)��amYc[o.:>?:;��-Q.�jŗÂ*��|&@i�
�7ɫk��EJ�91%�H~)��Hg�xH3�F��8o���&w{
S"W^�H'����m�����M�� �,�jx�H���X�tY(�p��^%]l��TȢ�~r%g?���M%畈���-������/�9nf�-�J���M�b��DZ9[�����Ӓ �Z�7�ղJ�~��b�t�c�ƍݤa��%P�"G�5�L4�Z`+���Y�X����@`�����8rQS���f� k|@��|"&�� `JJ��
���m$V��<\;��3�v=���\�.;���(MΎ� �  �۠�f�~�����8��$�؄�h����"gkb9�4H�Z���,Md"������(����`��Ty����}k�������z��1�l��ٛZ�@/�K��̅����9��M6�� �ۣ����+����)�1{�T��ì��X�z'�2�����̀\D6DY�ʍ�9ʥM2<�9�At���#���
� ��8d��qU�7�\�p�Nf�dt�Y8s2��<?r�/#�լ��V���T�Q��̩��~��҅7���:~sc�+�R@ɣZ���Ꮁ����q�D���	P�Qn�\7=������@����r�)�vq��m����=tld���#)���n�4�7���ԉѺ���2;�	-LD����Tg��^j	o���m�q0�r�0�S�}7o���t2;��H�q0��s;"MIlbPC�d����B}�7��/ 6�6Jb
����5G�����$z�
�::����6��$Ӟ���G?��M���m~ˁ���gs��t+�Z�v�s�;/�=H��V���o��]���������z6��I|m���o1�����Xqc(��^���p#��UĨ��a�o��?�m�}�P���0�́0��n��2�;��g��1_�����&�+�g�q�%��
&j�M)�$0_\��}/@YѾ �^gLr����a��g3:�$)iJ�I-�.D���#���+�<�,կ��7`�C��oN�1���A����OJ~y����/��޺-���GO���{��]�����i�s���"��! ^.��*�P��x,�[�NJ-OV7����j`ɓ�.5p!�����!��MT���$���8IPz�D���{S�TG}�O��R�%��%�7������49�����ӑ�C_��sb�����`R�
�)k��V�/�`�_�F�I�FSQ��p?����C͸�:�J]δ�$������%j��b9a �.F�P�t"q�N�;X����9�߂����J�i��T�KK��s*����VJQ��tZ^�4�oy���Rf��VU��n3-�0�tV��&Uh�m�_�"(%��j{i��|�DJGN1\�1������,�e�Ssc��0�i,E�тT���?��|cd5��Qt=_YT�OoX��u}�'v�8�U�/���Ϸ��5Ҳ�?�qZ��i�)�PyB�=��F����Qi��ka|��U"T�
�A�-�CK�7L���`�d/��B2�CH�#�#�����Dikr)�������랛���`$'�3�@�6v#�0�V-9g�ߩv���Z+\�5�pЂ�'4�p��qdN1�t/�4Cw�4��T�R��Yϵ��%�O){n ό�5��X�1 (VL(P4]��2��֊��F-.��Ǒ���W�Hn���� J�x�{_"�,�����BʮE�4��K�������K�*ƞAKC�%���J����L��M�eY�UA&ē��9��/���<::�_����      D   4   x�3�,��,K,I��2���OI-J,�/�2�LL����2��/�K-����� A4      F   )  x�mV�nk9\�|�!�%��!��Hj�c;���鯟r&3�݀l_���->n���t+��a��mZ���E�i��s�jmh_>�&+�3����P���׫^��
�=·��z�L9%դ\��L���Ө�#����8K�����:�ȝ�W���ڕ���x;�����M�5IYh9��x�3�O4kii�4h�O�IL%-wiUK/9���_=�v�<�m^oq:�����U2��R������/�Rma"J�,��7[5iI�k�Q�{�a���~�8\�7�X*>�x�6V��ޣX[+,���VN-W�S+,��Qʉ��o�������=�v<m=��j�-	v��*��Z�*Rdeim��V�!���v��?�?_��Q�o/��X���un�ro\@Z��gṆQS���-&I�3\c,c#\��@Ʋ��2��:����ib_5<5��[K#U�)�+����i��(�.���ܧ��kW��v�_W�9n(�D�:��T�����jΑi�ed��ƞ��6ȋ=��v�"�.ͼ��U�Y33eb�G��>��pД�<0�Kp�E̕����􈶔s��b��~�����||��Z��Eв�l���-h���� �\�����6#ֆ������7����ׯJe{���<�����ZTU,M`&�\*&B�JBMp��g� >�����#זj߃=_P��ʷ�|ަ��̄cM%r�,C7�:Kx�J�{�BCC��Qq�<�M�?�~����'�Fs�>n�'ݠ6�<�S�YE�d�M��E`/��R�Q�Met0] �1���۳�m+��?���GدM:.�P��>f���s�l+�����k6^3��4G@0�u���O�=���z��9���q.��.�B�0,]*;NSS�A�}�P���+9���'�����O��P����}`}_N���Ek^cvT��Fp���\�rda%����9������'Lھ'E�<�4�T4�XY;V6���+��2pi���y�����nw(��;��������]���:�@�d=�U�/ �B��Q�\��P]��Ғ������m8��I!���_%�f	���]�$�tמ��>�z�i�0�l�ޑu�������%�V�����~��X	>Ԑ���Q����TH����o��i���'�ӿ?�~�n�2 P�0,�&}�7�UF����U
�8�[�J�n��;���惓����A����+��ǪX|���YlṰ�;PB�4؄�-���G*�7�nwe��G�|�`<f2�bjh�cU`d�#����5�LVs��x8������q/�?OOO���D      J   �   x�M�1r!��N��A���F ��퍋M��ǩ����̓ ��8���wR�V��]�|-�&����e֎�5�6�Z��`[�\|����c�c=�uO�0#�3�3�6,J&�1���Ϻ����@.2�dD��GJ�V'6q��ej�m ��<H���h�j{�.��~��|���	h��$�*]�G�1�vH�      H   R   x����0�K1Q�G�^��}l���(�؄�#6b�P�w�#����1Ǥ��P�����ohc�-�H'����. ?L��     