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

LIST_QUERY_FILE = "queries/listGrants.rq"
DESCRIBE_QUERY_FILE = "queries/describeGrants.rq"
SUBJECT_NAME = "?grant"
INDEX = "unavco"
TYPE = "grant"
MAPPING = "mappings/grant.json"

# Second, extend the Ingest base class to class 'XIngest' below, where X is the singular form, with capitalized
# initial letter, of the 'type' of search document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with appropriate implementations.
# (Existing examples are helpful.)

class DatasetIngest(Ingest):

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
        #input(graph.serialize(format='turtle'))
        ds = graph.resource( entity )

        try:
            title = ds.label().toPython()
        except AttributeError:
            print( "missing title:", entity )
            return {}

        doc = {"uri": entity, "title": title}

        most_specific_type = list(ds.objects(VITRO.mostSpecificType))
        most_specific_type = most_specific_type[0].label().toPython() \
            if most_specific_type and most_specific_type[0].label() \
            else None
        if most_specific_type:
            doc.update({"mostSpecificType": most_specific_type})

        doi = list(ds.objects(BIBO.doi))
        doi = doi[0].toPython() if doi else None
        if doi:
            doc.update({"doi": doi})

        abstract = list(ds.objects(BIBO.abstract))
        abstract = abstract[0].toPython() if abstract else None
        if abstract:
            doc.update({"abstract": abstract})

        # cites
        cites = get_cites(ds)
        if cites:
            doc.update({"citations": cites})

        # PIs: if none, will return an empty list []
        pi = get_pi(ds,VIVO.PrincipalInvestigatorRole)
        doc.update({"principalInvestigator": pi})
        copi = get_pi(ds,VIVO.CoPrincipalInvestigatorRole)
        doc.update({"coPrincipalInvestigators": copi})

        # authors: if none, will return an empty list []
        sponsor_id = get_sponsor_id(ds)
        doc.update({"sponsorAwardId": sponsor_id})

        # date: if none, will return an empty list []
        publication_year = get_pub_year(ds)
        if publication_year:
            doc.update({"publicationYear": (publication_year)})
            
        # assigned_by: organization awarding grant
        assigned_by = get_assigned_by(ds)
        if assigned_by:
            doc.update({"assignedBy": (assigned_by)})
            
        # admin_org: grant administrator organization, usually same as PIs org
        admin_org = get_grant_admin(ds)
        if admin_org:
            doc.update({"administratingOrg": (admin_org)})
            
        # assigned_by: organization awarding grant
        start_date = get_start_date(ds)
        if start_date:
            doc.update({"startDate": (start_date)})

        return doc



# Third, pass the name of the sub-class just created above to argument 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=DatasetIngest)
if __name__ == "__main__":
    ingestSomething = DatasetIngest()
    ingestSomething.ingest()
