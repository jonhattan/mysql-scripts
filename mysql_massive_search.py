#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys
from re import search
import MySQLdb

cadena = '###CADENA DE BUSQUEDA###'

mycnf = os.path.expanduser('~/.my.cnf')
# pre-requisito
if not os.path.exists(mycnf):
    print "File %s must exist!" % mycnf
    sys.exit()

# cogemos usuario y contraseña
mysql_file = open(mycnf)
mycnf = mysql_file.read()
mysql_user = search('user\s+=\s+(.*)', mycnf).group(1)
mysql_passwd = search('password\s+=\s+(.*)', mycnf).group(1)
mysql_file.close()

# conectamos
db = MySQLdb.connect(host="localhost", user=mysql_user, passwd=mysql_passwd)
cursor = db.cursor()

# pedimos listado de todas las bases de datos
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()

# recorremos cada base de datos
for db in databases:
    db = db[0]
    print "Buscando en %s" % db
    # cargamos la bbdd actual y pedimos informacion del estado de cada tabla
    cursor.execute("USE `%s`" % db)
    cursor.execute("SHOW TABLE STATUS")
    tables = cursor.fetchall()

    # recorremos cada tabla para extraer la información y analizarla
    for table in tables:
        tablename = table[0]
        #print "  tabla %s" % tablename
        engine = table[1]
        if engine == "MEMORY": continue
        # cogemos todos los campos de la bbdd
        cursor.execute("DESCRIBE %s" % tablename)
        rows = cursor.fetchall()
        query = "SELECT count(*) FROM `%s` WHERE 1=0 " % tablename
        for row in rows:
            if row[1].startswith('date'): continue
            if row[1].startswith('time'): continue
            if row[1].startswith('int'): continue
            if row[1].startswith('float'): continue
            if row[1].startswith('numeric'): continue
            query += "OR `%s` LIKE '%%%s%%' " % (row[0], cadena)
        #print query +"\n"
        cursor.execute(query)
        r = cursor.fetchall()
        if r[0][0] > 0:
            print "Coincidencia en tabla %s.%s\n" % (db, tablename)
            print query

