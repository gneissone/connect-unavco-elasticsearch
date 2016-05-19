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

LIST_QUERY_FILE = "queries/listOrganizations.rq"
DESCRIBE_QUERY_FILE = "queries/describeOrganization.rq"
SUBJECT_NAME = "?organization"
INDEX = "unavco"
TYPE = "organization"

# Second, extend the Ingest base class to class 'XIngest' below, where X is the singular form, with capitalized
# initial letter, of the 'type' of search document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with appropriate implementations.
# (Existing examples are helpful.)

class OrganizationIngest(Ingest):
    
    MAPPING = "mappings/organization.json"
    
    def get_mapping( self ):
        return MAPPING

    def get_list_query_file(self):
        return LIST_QUERY_FILE

    def get_describe_query_file(self):
        return DESCRIBE_QUERY_FILE

    def get_subject_name(self):
        return SUBJECT_NAME

    def get_index(self):
        return INDEX

    def get_type(self):
        return TYPE

    def create_document( self, entity ):
        graph = self.describe_entity( entity )
        #print(graph.serialize(format='turtle'))
        ds = graph.resource( entity )

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

        org_role = list(ds.objects(OBO.RO_0000053))        
        for role in org_role:
            for role_type in role[RDF.type]:
                if role_type.identifier == VIVO.MemberRole:
                    doc.update({"membershipType": "Member"})
                    break 
                elif role_type.identifier == VLOCAL.AssociateMemberRole:
                    doc.update({"membershipType": "Associate Member"})
                    break

        #TODO add lookup state and country
        # authors: if none, will return an empty list []
        people = get_employees(ds)
        doc.update({"people": people})
        
        latlon = get_latlon(ds)
        if latlon:
            doc.update({"location": latlon})

        isni = get_isni(ds)
        doc.update({"isni": isni})

        grid = get_grid(ds)
        doc.update({"gridId": grid})

        return doc


# Third, pass the name of the sub-class just created above to argument 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=DatasetIngest)
if __name__ == "__main__":
    ingestSomething = OrganizationIngest()
    ingestSomething.ingest()
