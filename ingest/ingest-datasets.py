import functools
import argparse
import warnings
import pprint
import pydoc

# Import helper functions from ingestHelpers.py;
# see ingestHelpers.py for details of functions and classes used.
from ingestHelpers import *
from Ingest import *

# Please follow the comments below to create, customize and run the ingest
# process in you case.

# Start by create a copy of this script and rename it as appropriate.
# A uniform nomenclature is ingest-x.py where x is the plural form of the
# 'type' of search document generated.

# First, change these case-varying variables below for: dataset ingest

LIST_QUERY_FILE = "queries/listDatasets.rq"
DESCRIBE_QUERY_FILE = "queries/describeDataset.rq"
CONSTRUCT_QUERY_FILE = "queries/constructDataset.rq"
SUBJECT_NAME = "?dataset"
INDEX = "unavco"
TYPE = "dataset"
MAPPING = "mappings/dataset.json"

# Second, extend the Ingest base class to class 'XIngest' below, where X is
# the singular form, with capitalized initial letter, of the 'type' of search
# document generated. E.g. DatasetIngest, ProjectIngest, etc.
# Overwrite the subclass attribute 'MAPPING' and the create_x_doc method with
# appropriate implementations. (Existing examples are helpful.)


class DatasetIngest(Ingest):

    def get_mapping(self):
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

    MAPPING = "mappings/dataset.json"

    def create_document(self, entity):
        graph = self.describe_entity(entity)
        ds = graph.resource(entity)

        try:
            title = ds.label().toPython()
        except AttributeError:
            print("missing title:", entity)
            return {}

        doc = {"uri": entity, "title": title, "label": title}

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

        # authors: if none, will return an empty list []
        authors = get_authors(ds)
        doc.update({"authors": authors})

        # date: if none, will return an empty list []
        publication_year = get_pub_year(ds)
        if publication_year:
            doc.update({"publicationYear": (publication_year)})
        return doc


# Third, pass the name of the sub-class just created above to argument
# 'XIngest=' below in the usage of main().
#       E.g. main(..., XIngest=DatasetIngest)
if __name__ == "__main__":
    ingestSomething = DatasetIngest()
    ingestSomething.ingest()
