#!/bin/bash

# Iterate all databases and buid a query to add a default value
# to each column that doesn't have one and is a NOT NULL and not
# autoincremental one.
#
# Returns a list of queries.
#
# Usage:
#
#  ./mysql-columns-set-default.bash > /tmp/queries
#  cat /tmp/queries | mysql

MYSQL_VERSION=$(echo "select substring_index(version(), '-', 1);" | mysql --skip-column-names)

QUERIES=''
ROWS=$(mysql -s -e "SELECT C.TABLE_SCHEMA, C.TABLE_NAME, C.COLUMN_NAME, C.DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS C INNER JOIN INFORMATION_SCHEMA.TABLES T ON C.TABLE_NAME=T.TABLE_NAME AND T.TABLE_TYPE='BASE TABLE' WHERE C.IS_NULLABLE='NO' AND C.COLUMN_DEFAULT IS NULL AND C.EXTRA NOT LIKE '%auto_increment%' AND C.TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema')")


while read DATABASE TABLE COLUMN DATA_TYPE; do
  case $DATA_TYPE in
    # MySQL 8 BLOB and TEXT columns cannot have DEFAULT values. https://dev.mysql.com/doc/refman/8.0/en/blob.html
    # Before MariaDB 10.2.1, BLOB and TEXT columns could not be assigned a DEFAULT value. This restriction was lifted in MariaDB 10.2.1.
    *blob | *text)
      if [[ "$MYSQL_VERSION" > "10.2.1" ]]; then
        DEFAULT="''"
      else
        continue
      fi
      ;;
    *char)
      DEFAULT="''"
      ;;
    *binary)
      DEFAULT="''"
      ;;
    *int)
      DEFAULT=0
      ;;
    float)
      DEFAULT=0
      ;;
    decimal)
      DEFAULT=0
      ;;
    double)
      DEFAULT=0
      ;;
    date)
      DEFAULT="'0000-00-00'"
      ;;
    datetime)
      DEFAULT="'0000-00-00 00:00:00'"
      ;;
    enum) # defaults to the first element. strict mode doesn't complain
      continue
      ;;
    *)
      echo "# Unknown data type $DATA_TYPE for $DATABASE/$TABLE/$COLUMN"
      ;;
  esac
  QUERY="ALTER TABLE \`$DATABASE\`.\`$TABLE\` ALTER COLUMN \`$COLUMN\` SET DEFAULT $DEFAULT;"
  QUERIES="$QUERIES\n$QUERY"
done < <(echo $ROWS | xargs -n4)

echo -e $QUERIES;
