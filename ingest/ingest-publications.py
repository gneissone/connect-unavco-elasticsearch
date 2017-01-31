import functools
import argparse
import warnings
import pprint
import pydoc
import time

# Import helper functions from ingestHelpers.py;
# see ingestHelpers.py for details of functions and classes used.
from ingestHelpers import *
from Ingest import *

# Please follow the comments below to create, customize and run the ingest process in you case.

# Start by create a copy of this script and rename it as appropriate. A uniform nomenclature is
# ingest-x.py where x is the plural form of the 'type' of search document generated.

# First, change these case-varying variables below for: dataset ingest

LIST_QUERY_FILE = "queries/listPublications.rq"
DESCRIBE_QUERY_FILE = "queries/describePublication.rq"
CONSTRUCT_QUERY_FILE = "queries/constructPublication.rq"
SUBJECT_NAME = "?publication"
INDEX = "unavco"
TYPE = "publication"
MAPPING = "mappings/publication.json"
ALTMETRIC_API_KEY = '***REMOVED***'

def get_altmetric_for_doi(ALTMETRIC_API_KEY, doi):
    if doi:
        query = 'http://api.altmetric.com/v1/doi/' + doi + '?key=' + ALTMETRIC_API_KEY

        r = requests.get(query)
        if r.status_code == 200:
            try:
                json = r.json()
                time.sleep(1)
                print(json['score'])
                return json['score']
            except ValueError:
                logging.exception("Could not parse Altmetric response. ")
                return None
        elif r.status_code == 420:
            logging.info("Rate limit in effect!!!!")
            time.sleep(5)
        elif r.status_code == 403:
            logging.warn("Altmetric says you aren't authorized for this call.")
            return None
        else:
            logging.debug("No altmetric record or API error. ")
            return None
    else:
        return None


# Second, extend the Ingest base class to class 'XIngest' below, where X is the singular form, with capitalized
# initial letter, of the 'type' of search document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with appropriate implementations.
# (Existing examples are helpful.)

class PublicationIngest(Ingest):

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
        #graph = self.describe_entity( entity )
        #print(graph.serialize(format='turtle'))
        ds = self.graph.resource( entity )
        #print(graph.serialize(format='turtle'))
        try:
            title = ds.label().toPython()
        except AttributeError:
            print( "missing title:", entity )
            return {}

        doc = {"uri": entity, "title": title, "label": title}

        most_specific_type = list(ds.objects(RDF.type))
        most_specific_type = most_specific_type[0].label().toPython() \
            if most_specific_type and most_specific_type[0].label() \
            else None
        if most_specific_type:
            print(most_specific_type)
            doc.update({"mostSpecificType": most_specific_type})
        doi = list(ds.objects(BIBO.doi))
        doi = doi[0].toPython() if doi else None
        if doi:
            doc.update({"doi": doi})
        if self.altmetric:
            ams = get_altmetric_for_doi(ALTMETRIC_API_KEY, doi)
            doc.update({"amscore": ams})

        abstract = list(ds.objects(BIBO.abstract))
        abstract = abstract[0].toPython() if abstract else None
        if abstract:
            doc.update({"abstract": abstract})

        if abstract and not title:
            print(ds + 'is all jacked up')

        # projects
        projects = get_projects_of_dataset(ds)
        if projects:
            doc.update({"projects": projects})

        # dataType
        data_types = get_data_types(ds)
        if data_types:
            doc.update({"dataTypes": data_types})

        # cites
        cites = get_cites(ds)
        if cites:
            doc.update({"citations": cites})

        # related stations
        rel_stations = get_rel_stations(ds)
        if rel_stations:
            doc.update({"stations": rel_stations})

        # publication venue
        pub_venue = get_pub_venue(ds)
        if pub_venue:
            doc.update({"publishedIn": pub_venue})

        # authors: if none, will return an empty list []
        authors = get_authors(ds)
        doc.update({"authors": authors})

        # date: if none, will return an empty list []
        publication_year = get_pub_year(ds)
        if publication_year:
            doc.update({"publicationYear": (publication_year)})

        subject_areas = get_subject_areas(ds)
        if subject_areas:
            doc.update({"subjectArea": subject_areas})

        presented_at = get_presented_at(ds)
        if presented_at:
            doc.update({"presentedAt": presented_at})
        return doc


# Third, pass the name of the sub-class just created above to argument 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=DatasetIngest)
if __name__ == "__main__":
    ingestSomething = PublicationIngest()
    ingestSomething.ingest()
