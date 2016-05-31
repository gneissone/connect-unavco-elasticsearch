__author__ = 'Hao'

from rdflib import Namespace, RDF
from itertools import chain
import argparse
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import logging
from datetime import datetime

from rdflib import Namespace, RDF
PROV = Namespace("http://www.w3.org/ns/prov#")
BIBO = Namespace("http://purl.org/ontology/bibo/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITRO = Namespace("http://vitro.mannlib.cornell.edu/ns/vitro/0.7#")
VITRO_PUB = Namespace("http://vitro.mannlib.cornell.edu/ns/vitro/public#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
EC = Namespace("https://library.ucar.edu/earthcollab/schema#")
DCO = Namespace("http://info.deepcarbon.net/schema#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
RDFS = Namespace("http://www.w3.org/ns/dcat#")
CITO = Namespace("http://purl.org/spar/cito/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
VLOCAL = Namespace("http://connect.unavco.org/ontology/vlocal#")
WGS84 = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")

# Auxilary class for those helper functions getting attributes of objects
from Maybe import *

# standard filters
non_empty_str = lambda s: True if s else False
has_label = lambda o: True if o.label() else False

log = logging.getLogger(__name__)


def load_settings():
    try:
        with open('api_settings.json') as f:
            try:
                data = json.load(f)
                return data
            except Exception:
                logging.exception("Could not load API credentials. "
                                  "The api_settings.json file is likely "
                                  "not formatted correctly. See "
                                  "api_settings.json.example.")
                raise
    except Exception:
        logging.exception("Could not load API credentials. "
                          "Ensure your credentials and API stored "
                          "correctly in api_settings.json. See "
                          "api_settings.json.example.")
        raise

def load_file(filepath):
    """
    Helper function to load the .rq files and return a String object w/ replacing '\n' by ' '.
    :param filepath:    file path
    :return:            file content in string format
    """
    with open(filepath) as _file:
        return _file.read().replace('\n', " ")

def sparql_select(endpoint, query):
    """
    Helper function used to run a sparql select query
    :param endpoint:    SPARQL endpoint
    :param query:       the SPARQL query to get the list of objects
    :return:
        a list of objects with its type and uri values, e.g.
            [{'dataset': {'value': 'http://...', 'type': 'uri'}}, ...]
    """
    data = load_settings()
    try:
        EMAIL = data["api_user"]
        PASSWORD = data["api_password"]
        endpoint = data["query_api_url"]
    except KeyError:
        logging.exception("Could not load API credentials. "
                          "Ensure your credentials and API stored "
                          "correctly in api_settings.json. See "
                          "api_settings.json.example.")
        raise RuntimeError('Update failed. See log for details.')
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    sparql.addParameter("email", EMAIL)
    sparql.addParameter("password", PASSWORD)
    results = sparql.query().convert()
    return results["results"]["bindings"]

# describe: helper function for describe_entity
def sparql_describe( endpoint, query ):
    """
    Helper function used to run a sparql describe query
    :param endpoint:    SPARQL endpoint
    :param query:       the describe query to run
    :return:
        a json object representing the entity
    """
    data = load_settings()
    try:
        EMAIL = data["api_user"]
        PASSWORD = data["api_password"]
        API_URL = data["query_api_url"]
    except KeyError:
        logging.exception("Could not load API credentials. "
                          "Ensure your credentials and API stored "
                          "correctly in api_settings.json. See "
                          "api_settings.json.example.")
        raise RuntimeError('Update failed. See log for details.')
    sparql = SPARQLWrapper( endpoint )
    sparql.setQuery( query )
    sparql.setMethod("POST")
    sparql.addParameter("email", EMAIL)
    sparql.addParameter("password", PASSWORD)
    try:
        r = sparql.query().convert()
        #print(r.serialize(format="turtle"))
        return r
    except RuntimeWarning:
        pass

def get_id( es_id ):
    return dco_id[dco_id.rfind('/') + 1:]

def get_metadata( es_index, es_type, es_id ):
    """
    Helper function to create the JSON string of the metadata of an entity.
    :param id:      unique identifier of the entity
    :return:
        a JSON-format string representing the metadata information of the object,
            e.g. {"index": {"_id": "http://...", "_type": "dataset", "_index": "dco"}}
    """
    return {"index": {"_index": es_index, "_type": es_type, "_id": get_id( es_id )}}

###################################################
#    Helper functions to get different attributes
#
def has_type(resource, type):
    for rtype in resource.objects(RDF.type):
        if str(rtype.identifier) == str(type):
            return True
    return False

def has_most_specific_type(resource, type):
    for rtype in resource.objects(VITRO.mostSpecificType):
        if str(rtype.identifier) == str(type):
            return True
    return False

def get_id(dco_id):
    return dco_id[dco_id.rfind('/') + 1:]


def get_dco_communities(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(DCO.associatedDCOCommunity)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()


def get_data_types(x):
     return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(EC.hasDatasetType)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_cites(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(CITO.isCitedAsDataSourceBy)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
        
def get_rel_stations(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(OBO.RO_0002353)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_rel_datasets(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(OBO.RO_0002234)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_projects_of_dataset(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(DCO.isDatasetOf)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
        
def get_pub_venue(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(VIVO.hasPublicationVenue)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
        
def get_isni(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(VLOCAL.isni)) \
        .filter(non_empty_str) \
        .one().value

def get_grid(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(VIVO.gridId)) \
        .filter(non_empty_str) \
        .one().value

def get_latlon(x):
    lat = Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(WGS84.lat)) \
        .filter(non_empty_str) \
        .one().value

    lon = Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(WGS84.long)) \
        .filter(non_empty_str) \
        .one().value
        
    if lat and lon:
        return({"lat": float(lat), "lon": float(lon)})
    else:
        return None

def get_sponsor_id(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(VIVO.sponsorAwardId)) \
        .filter(non_empty_str) \
        .one().value

def get_presented_at(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(BIBO.presentedAt)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_pi(x, role):
    pis = []
    pi_roles = [faux for faux in x.objects(VIVO.relates) if has_type(faux, role)]
    for pi_role in pi_roles:
        author = [person for person in pi_role.objects(OBO.RO_0000052) if has_type(person, FOAF.Person)]
        if author:
            author = author[0]
        vcard = [person for person in pi_role.objects(OBO.RO_0000052) if has_type(person, VCARD.Individual)]
        if vcard:
            vcard = vcard[0]
        if author:
            name = author.label().toPython()
            obj = {"uri": str(author.identifier), "name": name}
            research_areas = [research_area.label().toPython() for research_area in author.objects(VIVO.hasResearchArea) if research_area.label()]
            if research_areas:
                obj.update({"researchArea": research_areas})
        elif vcard:
            vList = [faux for faux in vcard.objects(VCARD.hasName)][0]
            if list(vList.objects(VCARD.familyName)):
                fName = str(list(vList.objects(VCARD.familyName))[0])
            else:
                fName = None
            if list(vList.objects(VCARD.givenName)):
                gName = str(list(vList.objects(VCARD.givenName))[0])
            else:
                gName = None

            if fName and gName:
                name = '{}, {}'.format(fName,gName)
            elif fName and not gName:
                name = '{}'.format(fName)
            elif gName and not fName:
                name = '{}'.format(gName)
            else:
                name = None
            obj = {"uri": None, "name": name}
        else:
            name = None

        pis.append(obj)
    return pis

# get_authors: object -> [authors] for objects such as: datasets, publications, ...
def get_authors(ds):
    authors = []
    authorships = [faux for faux in ds.objects(VIVO.relatedBy) if has_type(faux, VIVO.Authorship)]
    for authorship in authorships:  
        author = [person for person in authorship.objects(VIVO.relates) if has_type(person, FOAF.Person)]
        if author:
            author = author[0]
        vcard = [person for person in authorship.objects(VIVO.relates) if has_type(person, VCARD.Individual)]
        if vcard:
            vcard = vcard[0]    
        if author:
            name = author.label().toPython()
            obj = {"uri": str(author.identifier), "name": name}
            org = list(author.objects(DCO.inOrganization))
            org = org[0] if org else None
            if org and org.label():
                obj.update({"organization": {"uri": str(org.identifier), "name": org.label().toPython()}})
            research_areas = [research_area.label().toPython() for research_area in author.objects(VIVO.hasResearchArea) if research_area.label()]
            if research_areas:
                obj.update({"researchArea": research_areas})
        elif vcard:
            vList = [faux for faux in vcard.objects(VCARD.hasName)][0]
            if list(vList.objects(VCARD.familyName)):
                fName = str(list(vList.objects(VCARD.familyName))[0])
            else:
                fName = None
            if list(vList.objects(VCARD.givenName)):
                gName = str(list(vList.objects(VCARD.givenName))[0])
            else:
                gName = None

            if fName and gName:
                name = '{}, {}'.format(fName,gName)
            elif fName and not gName:
                name = '{}'.format(fName)
            elif gName and not fName:
                name = '{}'.format(gName)
            else:
                name = None
            obj = {"uri": None, "name": name}
        else:
            name = None

        rank = list(authorship.objects(VIVO.rank))
        rank = str(rank[0].toPython()) if rank else None # added the str()
        if rank:
            obj.update({"rank": rank})

        authors.append(obj)


    try:
        authors = sorted(authors, key=lambda a: a["rank"]) if len(authors) > 1 else authors
    except KeyError:
        print("missing rank for one or more authors of:", ds)

    return authors
    
def get_employees(ds):
    pers = []
    ended = False
    liaisons = list(ds.objects(VLOCAL.hasLiaison))

    roles = Maybe.of(ds).stream() \
        .flatmap(lambda per: per.objects(VIVO.relatedBy)) \
        .filter(lambda related: has_type(related, VIVO.Position)).list()

    for role in roles:
        # Only add a person as an employee if the position is current
        # It is faster to determine this here rather than with SPARQL filters
        ended = False
        dtList = [faux for faux in role.objects(VIVO.dateTimeInterval)]
        for dates in dtList:
            endDates = list(dates.objects(VIVO.end))
            if endDates :
                ended = True
                break

        if not ended:
            person = Maybe.of(role).stream() \
                     .flatmap(lambda r: r.objects(VIVO.relates)) \
                     .filter(lambda o: has_type(o, FOAF.Person)) \
                     .filter(has_label).one().value

            if person in liaisons:
                memberRep = 'true'
            else:
                memberRep = 'false'

            per = Maybe.of(role).stream() \
                .flatmap(lambda r: r.objects(VIVO.relates)) \
                .filter(lambda o: has_type(o, FOAF.Person)) \
                .filter(has_label) \
                .map(lambda o: {"uri": str(o.identifier), "name": str(o.label()), 
                "unavcoMemberRep": memberRep, "position": str(role.label())}) \
                .one().value

            if per:
                pers.append(per)

    return pers    
    
# get_authors: object -> [authors] for objects such as: datasets, publications, ...
def get_pub_year(ds):
    dtList = []
    date = None
    #dtObj = ds.objects(VIVO.dateTimeValue)
    dtList = [faux for faux in ds.objects(VIVO.dateTimeValue)]
    for dates in dtList:
        date = list(dates.objects(VIVO.dateTime))
        date = str(date[0]) if date else None

    if date:
        return date
    else:
        return None

def get_data_typesasdasdad(ds):
    dtList = []
    dtList = [faux for faux in ds.objects(EC.hasDatasetType)]
    for types in dtList:
        data_type = str(list(types.objects(RDFS.label))[0])

    #pubdate = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    # TODO Get and return the publication date!

    if data_type:
        return data_type
    else:
        return None
        
        
def get_subject_areas(ds):
    subject_areas = []
    for subject_area in ds.objects(VIVO.hasSubjectArea):
        sa = {"uri": str(subject_area.identifier)}
        if subject_area.label():
            sa.update({"name": subject_area.label().toPython()})
        subject_areas.append(sa)


    return subject_areas
    
    
def get_sub_orgs(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(OBO.BFO_0000051)) \
        .filter(lambda partof: has_type(partof, FOAF.Organization)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_super_orgs(x):
    return Maybe.of(x).stream() \
        .flatmap(lambda p: p.objects(OBO.BFO_0000050)) \
        .filter(lambda partof: has_type(partof, FOAF.Organization)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
    
# get_distributions: object -> [distributions] for objects such as: datasets, publications, ...
def get_distributions(ds):
    distributions = []
    distributionList = [faux for faux in ds.objects(DCO.hasDistribution) if has_type(faux, DCAT.Distribution)]
    for distribution in distributionList:
        accessURL = str(list(distribution.objects(DCO.accessURL))[0])
        name = distribution.label().toPython() if distribution else None
        obj = {"uri": str(distribution.identifier), "accessURL": accessURL, "name": name}

        fileList = list(distribution.objects(DCO.hasFile))
        fileList = fileList if fileList else None
        files = []
        for file in fileList:
            downloadURL = list(file.objects(DCO.downloadURL))
            downloadURL = str(downloadURL[0]) if downloadURL else None
            fileObj = {"uri": str(file.identifier),
                       "name": file.label().toPython()}
            fileObj.update({"downloadURL": downloadURL})
            files.append(fileObj)

        if files:
            obj.update({"files": files})

        distributions.append(obj)

    return distributions
    
def get_grant_admin(x):
    return Maybe.of(x).stream() \
             .flatmap(lambda r: r.objects(VIVO.relates)) \
             .filter(lambda o: has_type(o, FOAF.Organization)) \
             .filter(has_label) \
             .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
             
def get_assigned_by(x):
    return Maybe.of(x).stream() \
             .flatmap(lambda r: r.objects(VIVO.assignedBy)) \
             .filter(lambda o: has_type(o, FOAF.Organization)) \
             .filter(has_label) \
             .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()

def get_start_date(ds):
    return Maybe.of(ds).stream() \
            .flatmap(lambda dti: dti.objects(VIVO.dateTimeInterval)) \
            .flatmap(lambda sd: sd.objects(VIVO.start)) \
            .flatmap(lambda dt: dt.objects(VIVO.dateTime)) \
            .filter(non_empty_str) \
            .one().value

def get_thumbnail(ds):
    return Maybe.of(ds).stream() \
        .flatmap(lambda p: p.objects(VITRO_PUB.mainImage)) \
        .flatmap(lambda i: i.objects(VITRO_PUB.thumbnailImage)) \
        .flatmap(lambda t: t.objects(VITRO_PUB.downloadLocation)) \
        .map(lambda t: t.identifier) \
        .one().value

# level should be the URI of a place class
def get_location(ds,level='http://vivoweb.org/ontology/core#GeographicLocation'):
    return Maybe.of(ds).stream() \
        .flatmap(lambda p: p.objects(OBO.BFO_0000050)) \
        .filter(lambda partof: has_most_specific_type(partof, level)) \
        .filter(has_label) \
        .map(lambda r: {"uri": str(r.identifier), "name": str(r.label())}).list()
