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

LIST_QUERY_FILE = "queries/listPeople.rq"
DESCRIBE_QUERY_FILE = "queries/describePerson.rq"
SUBJECT_NAME = "?person"
INDEX = "unavco"
TYPE = "person"
MAPPING = "mappings/person.json"

# Second, extend the Ingest base class to class 'XIngest' below, where X is the singular form, with capitalized
# initial letter, of the 'type' of search document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with appropriate implementations.
# (Existing examples are helpful.)

class PersonIngest(Ingest):

    def get_mapping( self ):
        return MAPPING

    def get_list_query_file(self):
        return LIST_QUERY_FILE

    def get_describe_query_file(self):
        return DESCRIBE_QUERY_FILE
        
    def get_construct_query_file(self):
        return DESCRIBE_QUERY_FILE

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
            
        orcid = get_orcid(ds)
        if orcid:
            doc.update({"orcid": orcid})
            
        given_name = get_given_name(ds)
        if given_name:
            doc.update({"givenName": given_name})

        family_name = get_family_name(ds)
        if family_name:
            doc.update({"familyName": family_name})

        email = get_email(ds)
        if email:
            doc.update({"email": email})

        research_areas = get_research_areas(ds)
        if research_areas:
            doc.update({"researchArea": research_areas})
            
        expertise_areas = get_expertise_areas(ds)
        if expertise_areas:
            doc.update({"expertiseArea": expertise_areas})        

        organizations = get_organizations(ds)
        if organizations:
            doc.update({"organizations": organizations})

        thumbnail = get_thumbnail(ds)
        if thumbnail:
            doc.update({"thumbnail": thumbnail})

            
        thumbnail = get_thumbnail(ds)
        if thumbnail:
            doc.update({"thumbnail": thumbnail})
            
        

        return doc



# Third, pass the name of the sub-class just created above to argument 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=StationIngest)
if __name__ == "__main__":
    ingestSomething = PersonIngest()
    ingestSomething.ingest()
