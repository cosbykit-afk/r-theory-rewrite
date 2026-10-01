#!/bin/sh
# Reassemble the chunked zip: sh reassemble.sh
cat rtheory-tables.zip.part-* > rtheory-tables.zip
unzip -o rtheory-tables.zip
