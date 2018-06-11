#!/usr/bin/python -tt
# -*- coding: UTF-8 -*-

# by jonhattan <jonhattan@faita.net>
# 03 / Mar / 2010 :: 11:30

import os, sys
from re import search
import MySQLdb


class Database:
    host = None
    user = None
    passwd = None
    db_name = None
    db_charset = None
    db_collation = None
    link = None
    cursor = None

    def __init__(self, host = 'localhost', user = None, passwd = None, db_name = None):
        self.host = host
        # credentials
        if user is not None:
            self.user = user
            self.passwd = passwd
        else:
            mycnf = os.path.expanduser('~/.my.cnf')
            # pre-requisite
            if not os.path.exists(mycnf):
                print "File %s must exist!" % mycnf
                sys.exit()

            # get user and password to connect to the database
            mysql_file = open(mycnf)
            mycnf = mysql_file.read()
            self.user = search('user\s+=\s+(.*)', mycnf).group(1)
            self.passwd = search('password\s+=\s+(.*)', mycnf).group(1)
            mysql_file.close()

        # connect the server
        self.link = MySQLdb.connect(host= host, user = self.user, passwd = self.passwd)
        self.cursor = self.link.cursor()
        self.show_server_defaults()

        # select database
        if db_name is None:
            db_name = self._choose_database()
        self.db_name = db_name
        self.link.select_db(self.db_name)
        self.show_database_defaults()


    def show_server_defaults(self):
        info = self.link.get_character_set_info()
        print "== Server Info =="
        print "  Default character set: %s" % info['name']
        print "  Default collation: %s" % info['collation']
        print


    def show_database_defaults(self):
        query = "SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '%s' LIMIT 1" % self.db_name;
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        self.db_charset = data[0][0]
        self.db_collation = data[0][1]
        print "== Database Info =="
        print "  Charset:   %s\t\t\t(tables may have a different charset)" % self.db_charset
        print "  Collation: %s\t\t(tables may have a different collation)" % self.db_collation
        print

    
    def _choose_database(self):
        cursor = self.link.cursor()
        cursor.execute("SHOW DATABASES")
        databases = dict()
        print "== Available Databases =="
        for i, db in enumerate(cursor.fetchall()):
            db_name = db[0]
            if db_name == 'information_schema':
              continue
            databases[i] = db_name
            print "%03s: %s" % (i, db_name)
        print

        option = -1
        while option not in databases.keys():
            print "Choose the database to operate on:"
            option = int(sys.stdin.readline())
        print
        return databases[option]


    def select_collation(self, charset, collation):      
        """
        Given a charset, allow to select a collation compatible with the charset.
        The list of available collations will exclude the collation passed as parameter.
        """
#        query = "SHOW COLLATION WHERE CHARSET = '%s' AND COLLATION != '%s'" % (charset, collation)
        query = "SHOW COLLATION WHERE CHARSET = '%s'" % (charset, )
        cursor = self.link.cursor()
        cursor.execute(query)
        collations = dict()
        print "== Collations compatibles with charset %s ==" % charset
        for i, collation in enumerate(cursor.fetchall()):
            collations[i] = collation[0]
            print "%03s: %s" % (i, collation[0])
        print

        option = -1
        while option not in collations.keys():
            print "Choose collation to apply to database:"
            option = int(sys.stdin.readline())
        print
        return collations[option]


    def change_database_collation(self, collation):
        """
        Alters the database to change the collation.
        """
        print "Changing collation for database %s" % self.db_name
        self.db_collation = collation
        query = "ALTER DATABASE `%s` DEFAULT CHARACTER SET %s COLLATE %s" % (self.db_name, self.db_charset, self.db_collation)
        self.cursor.execute(query)

        # now iterate over the tables and change collation one by one
        self.cursor.execute("SHOW TABLE STATUS")
        tables = self.cursor.fetchall()
        for table in tables:
            engine = table[1]
            if engine not in ('MyISAM', 'InnoDB'):
                continue
            ###### TODO: how to obtain the table charset? does it make sense?
            self.change_table_collation(table[0], collation)


    def change_table_collation(self, table, collation):
        print "Changing collation for table %s" % table
        # table
        query = "ALTER TABLE `%s` DEFAULT CHARACTER SET %s COLLATE %s" % (table, self.db_charset, collation)
        self.cursor.execute(query)
        # rows
        query = "SELECT COLUMN_NAME,CHARACTER_SET_NAME FROM information_schema.columns WHERE table_schema='%s' AND table_name='%s' AND COLLATION_NAME IS NOT NULL" % (self.db_name, table)
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            assert (row[1] == self.db_charset), "Charset of column %s (%s) doesn't match with database charset (%s)" % (row[0], row[1], self.db_charset)
            self.change_row_collation(table, row[0], collation)
    
    def change_row_collation(self, table, row, collation):
        print "Changing collation for row %s" % row
        query = "SELECT column_name,column_type FROM information_schema.columns WHERE table_schema='%s' AND table_name='%s' AND column_name='%s' LIMIT 1" % (self.db_name, table, row)
        self.cursor.execute(query)
        row = self.cursor.fetchall()
        row = row[0]
        query = "ALTER TABLE `%s` CHANGE `%s` `%s` %s CHARACTER SET %s COLLATE %s" % (table, row[0], row[0], row[1], self.db_charset, collation)
        self.cursor.execute(query)

if __name__ == '__main__':
    dbserver = Database(db_name='qubit_archivo_108')
#    collation = dbserver.select_collation(dbserver.db_charset, dbserver.db_collation)
    dbserver.change_database_collation('latin1_spanish_ci')

