#!/bin/sh

##############
# People
##############

echo "**** Start People Ingest"
ofile=`date +"%Y%m%d-%H-%M-%S".people.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-people.py --limit 50000 --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --es http://localhost:9200 --redbuild --publish ${ofile} >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/people-ingest.log

gzip ${ofile}
mv ${ofile}.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups
echo "**** End People Ingest"
sleep 30

##############
# Grants
##############

echo "**** Start Grant Ingest"
ofile=`date +"%Y%m%d-%H-%M-%S".grants.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest 

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-grants.py --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --es http://localhost:9200 --rebuild  --publish $ofile >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/grants-ingest.log 

gzip $ofile
mv $ofile.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups/
echo "**** End Grant Ingest"
sleep 30

##############
# Organizations
##############

echo "**** Start Organization Ingest"
ofile=`date +"%Y%m%d-%H-%M-%S".organizations.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest 

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-organizations.py --limit 50000 --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --es http://localhost:9200 --publish $ofile >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/organizations-ingest.log 

gzip $ofile
mv $ofile.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups/
echo "**** End Organization Ingest"
sleep 30

##############
# Publications
##############

echo "**** Start Publications Ingest"
ofile=`date +"%Y%m%d-%H-%M-%S".publications.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest 

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-publications.py --limit 50000 --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --altmetric --es http://localhost:9200 --rebuild --publish $ofile >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/publication-ingest.log

gzip $ofile
mv $ofile.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups/
echo "**** End Publications Ingest"

##############
# Places
##############

echo "**** Start Places Ingest"

ofile=`date +"%Y%m%d-%H-%M-%S".places.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest 

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-stations.py --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --es http://localhost:9200 --rebuild --publish $ofile >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/station-ingest.log

gzip $ofile

mv $ofile.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups/

##############
# Dataset
##############

echo "**** Start Dataset Ingest"
ofile=`date +"%Y%m%d-%H-%M-%S".dataset.bulk`

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest 

/usr/local/bin/python3 /usr/local/scripts/connect-unavco-elasticsearch/ingest/ingest-datasets.py --limit 50000 --threads 4 --sparql http://vivodev.int.unavco.org/vivo/api/sparqlQuery --es http://localhost:9200 --rebuild --publish $ofile >> /usr/local/scripts/connect-unavco-elasticsearch/ingest/logs/dataset-ingest.log

gzip $ofile

mv $ofile.gz /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups/

##############
# Cleanup
##############

cd /usr/local/scripts/connect-unavco-elasticsearch/ingest/backups
find . -atime +5 -delete
