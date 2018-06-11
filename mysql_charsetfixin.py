#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
from sys import stdin, exit

map_raro_bueno = {# tildes
				  u'Ã¡': u'á',
				  u'Ã©': u'é',
				  u'Ã­': u'í',
				  u'Ã³': u'ó',
				  u'Ãº': u'ú',
				  u'Ã': u'Á',
				  u'Ã': u'É',
				  u'Ã': u'Í',
				  u'Ã': u'Ó',
				  u'Ã': u'Ú',
				  # ñ y otros
				  u'Ã±': u'ñ',
				  u'Ã': u'Ñ',
				  u'Ã§': u'ç',
				  u'Â«': u'«',
				  u'Â»': u'»',
				  u'Â¿': u'¿',
				  u'lÂ·l': u'l·l',
				  u'Â¡': u'¡',
				  #u'â¬': u'€',
				  # la otra tilde
				  u'Ã ': u'à',
				  u'Ã¨': u'è',
				  u'Ã¬': u'ì',
				  u'Ã²': u'ò',
				  u'Ã¹': u'ù',
				  u'Ã': u'À',
				  u'Ã': u'È',
				  u'Ã': u'Ì',
				  u'Ã': u'Ò',
				  u'Ã': u'Ù',
				  # diéresis
#				  'Ã¤': u'ä',
#				  'Ã«': u'ë',
#				  'Ã¯': u'ï',
#				  'Ã¶': u'ö',
#				  'Ã¼': u'ü',
#				  'Ã': u'Ä',
#				  'Ã': u'Ë',
#				  'Ã': u'Ï',
#				  'Ã': u'Ö',
#				  'Ã': u'Ü',
				  }

print 'database: '
database = stdin.readline()[:-1]
print "user: "
user = stdin.readline()[:-1]
print "passwd: "
passwd = stdin.readline()[:-1]

db = MySQLdb.connect(host="localhost", user=user, passwd=passwd)
cursor = db.cursor()
cursor.execute("USE %s" % database)
cursor.execute("SHOW TABLES;")
tablas = cursor.fetchall()

for tabla in tablas:
	tabla = tabla[0]
	cursor.execute("DESCRIBE %s" % tabla)
	campos = cursor.fetchall()
	for campo in campos:
		tipo = campo[1]
		campo = campo[0]
		if tipo.startswith('varchar') or tipo in('longtext', 'text'):
			print "trabajando sobre %s.%s" % (tabla, campo)
			for raro, bueno in map_raro_bueno.iteritems():
				query = u"update %s set %s = replace(%s, '%s', '%s');" % (tabla, campo, campo, raro, bueno)
				print "    ", query
				try: # puede ocurrir que al arreglar xxxÃ¡ -> xxxá. si ese txt es de un campo UNIQUE, cante un errorzillo "duplicate entry"
					cursor.execute(query)
				except MySQLdb.IntegrityError:
					pass
				result = cursor.fetchall()
				if len(result) > 0:
					print "    ", result
					print "abortado."
					exit()
