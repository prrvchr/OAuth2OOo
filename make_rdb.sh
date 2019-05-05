#!/bin/bash

WorkBench=OAuth2OOo
OOoProgram=/usr/lib/libreoffice/program
Path=$(dirname "${0}")

rm ${Path}/${WorkBench}/types.rdb

./rdb/make_rdb.sh ${WorkBench} com/sun/star/auth/XOAuth2Service
./rdb/make_rdb.sh ${WorkBench} com/sun/star/auth/OAuth2Service

read -p "Press enter to continue"

${OOoProgram}/regview ${Path}/${WorkBench}/types.rdb
