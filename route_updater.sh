#!/bin/sh
MAIN_SET="minitruth"
TEMP_SET="_minitruth"
EXIST=`ipset -L -t | grep ${MAIN_SET}`
if [ -z "${EXIST}" ]; then
    ipset create ${MAIN_SET} hash:net maxelem 524288
    curl -s https://nullroute.mgdz.dev/data/100.txt | awk '{print "add '${MAIN_SET}' "$1;}' | ipset -! restore
else
    ipset create ${TEMP_SET} hash:net maxelem 524288
    curl -s https://nullroute.mgdz.dev/data/100.txt | awk '{print "add '${TEMP_SET}' "$1;}' | ipset -! restore
    ipset swap ${MAIN_SET} ${TEMP_SET}
    ipset destroy ${TEMP_SET}
fi
