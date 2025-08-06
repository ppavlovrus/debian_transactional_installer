#!/bin/bash
mkdir -p /var/www/testsite
sqlite3 /var/www/testsite/site.db "CREATE TABLE demo(id INTEGER PRIMARY KEY, val TEXT);" 