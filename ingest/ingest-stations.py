import functools
import argparse
import warnings
import pprint
import pydoc

# Import helper functions from ingestHelpers.py;
# see ingestHelpers.py for details of functions and classes used.
from ingestHelpers import *
from Ingest import *

# Please follow the comments below to create, customize and run the ingest process in you case.

# Start by create a copy of this script and rename it as appropriate. A uniform nomenclature is
# ingest-x.py where x is the plural form of the 'type' of search document generated.

# First, change these case-varying variables below for: dataset ingest

LIST_QUERY_FILE = "queries/listStations.rq"
DESCRIBE_QUERY_FILE = "queries/describeStation.rq"
CONSTRUCT_QUERY_FILE = "queries/constructStations.rq"
SUBJECT_NAME = "?station"
INDEX = "unavco"
TYPE = "station"
MAPPING = "mappings/station.json"

# Second, extend the Ingest base class to class 'XIngest' below, where X is the singular form, with capitalized
# initial letter, of the 'type' of search document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with appropriate implementations.
# (Existing examples are helpful.)

class StationIngest(Ingest):

    def get_mapping( self ):
        return MAPPING

    def get_list_query_file(self):
        return LIST_QUERY_FILE

    def get_describe_query_file(self):
        return DESCRIBE_QUERY_FILE

    def get_construct_query_file(self):
        return CONSTRUCT_QUERY_FILE

    def get_subject_name(self):
        return SUBJECT_NAME

    def get_index(self):
        return INDEX

    def get_type(self):
        return TYPE

    def create_document( self, entity ):
        ds = self.graph.resource( entity )

        try:
            title = ds.label().toPython()
        except AttributeError:
            print( "missing title:", entity )
            return {}

        doc = {"uri": entity, "name": title}

        most_specific_type = list(ds.objects(VITRO.mostSpecificType))
        most_specific_type = most_specific_type[0].label().toPython() \
            if most_specific_type and most_specific_type[0].label() \
            else None
        if most_specific_type:
            doc.update({"mostSpecificType": most_specific_type})
            
        fourChId = list(ds.objects(VLOCAL.has4CharID))
        fourChId = fourChId[0].value \
            if fourChId and fourChId[0].value \
            else None
        if fourChId:
            doc.update({"4ChId": fourChId})

        # PIs: if none, will return an empty list []
        pi = get_pi(ds,VIVO.PrincipalInvestigatorRole)
        doc.update({"principalInvestigators": pi})
        copi = get_pi(ds,VIVO.CoPrincipalInvestigatorRole)
        doc.update({"coPrincipalInvestigators": copi})

        start_date = get_start_date(ds)
        if start_date:
            doc.update({"startDate": (start_date)})
            
        thumbnail = get_thumbnail(ds)
        if thumbnail:
            doc.update({"thumbnail": thumbnail})
            
        # date: if none, will return an empty list []
        retirement_date = get_pub_year(ds)
        if retirement_date:
            doc.update({"retirementDate": (retirement_date)})
        
        datasets = get_rel_datasets(ds)
        if datasets:
            doc.update({"relatedDatasets": datasets})
        
        # Locations
        state = get_location(ds,'http://vivoweb.org/ontology/core#StateOrProvince')
        if state:
            doc.update({"state": (state)})

        country = get_location(ds,'http://vivoweb.org/ontology/core#Country')
        if country:
            doc.update({"country": (country)})

        continent = get_location(ds,'http://vivoweb.org/ontology/core#Continent')
        if continent:
            doc.update({"continent": (continent)})   

        return doc



# Third, pass the name of the sub-class just created above to argument 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=StationIngest)
if __name__ == "__main__":
    ingestSomething = StationIngest()
    ingestSomething.ingest()
