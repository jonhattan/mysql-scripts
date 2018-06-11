#!/usr/bin/python
# -*- coding: UTF-8 -*-

#by jonhattan <jon@sindominio.net>
# 12 / Oct / 2008 :: 11:36

import os, sys
from re import search
import MySQLdb

VERBOSE = False

# actions to perform
check_and_repair = True
optimize = True
alert_if_size_higher_than = 20 * 1024 * 1024 # bytes (False if no alert)

def human_metrics(bytes):
    if bytes > 1048576:
        result = "%s MB" % (bytes / 1048576.)
    elif bytes > 1024:
        result = "%s KB" % (bytes / 1024.)
    else:
        result = "%s bytes" % bytes
    return result
        

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
total_overhead = 0
for db in databases:
    dbname = db[0]
    if dbname == 'information_schema': 
        continue
    if VERBOSE: print "* database: %s" % dbname
    # cargamos la bbdd actual y pedimos informacion del estado de cada tabla
    cursor.execute("USE `%s`" % dbname)
    cursor.execute("SHOW TABLE STATUS")
    tables = cursor.fetchall()

    # recorremos cada tabla para extraer la información y analizarla
    db_overhead = 0
    for table in tables:
        if VERBOSE: print " * table: %s (engine %s)" % (table[0], table[1])
        tablename = table[0]
	data_length = table[6]
	data_free = table[9]
	# 1. checkear y reparar
	if check_and_repair:
	    engine = table[1]
	    if engine == 'MyISAM' or engine is None:
	        cursor.execute("CHECK TABLE `%s`" % tablename)
		result = cursor.fetchone()
		op, msg_type, msg_text = result[1:]
		if VERBOSE: print "  * ", op, msg_type, msg_text
		if msg_text != 'OK':
		    print "Trying to repair table %s" % tablename
	            cursor.execute("REPAIR TABLE `%s`" % tablename)
		    result = cursor.fetchone()
		    op, msg_type, msg_text = result[1:]
		    if VERBOSE: print "  * ", op, msg_type, msg_text
            else:
	        if VERBOSE: print u"  * Engine no soportado"
        # 2. optimizar la tabla si es necesario
	if optimize:
	    if data_free > 0:
                db_overhead += data_free
                size, overhead = map(human_metrics, (data_length, data_free))
	        print "%s.%s: %s of size. %s are unused and will be freed" % (dbname, tablename, size, overhead)
	        cursor.execute("OPTIMIZE TABLE `%s`" % tablename)
        # 3. alerta si la tabla tiene un tamaño grande
	if alert_if_size_higher_than is not False:
            if data_length > alert_if_size_higher_than:
	        size = human_metrics(data_length)
	        print "%s.%s: %s of size." % (dbname, tablename, size)
    if db_overhead > 0:
        print "Database %s has an overhead of: %s\n" % (dbname, human_metrics(db_overhead))
        total_overhead += db_overhead

if total_overhead > 0:
    print "** The total overhead is %s **" % (human_metrics(total_overhead))

