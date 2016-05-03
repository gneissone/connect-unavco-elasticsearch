## Usage and Examples of Running Your Ingest Process

### Usage:

    Arguments:
        --threads: number of threads to use (default = 4)
        --es', elasticsearch service URL (default="http://localhost:9200")
        --publish', publish to elasticsearch? (default=False)
        --rebuild', rebuild elasticsearch index? (default=False)
        --mapping', dataset elasticsearch mapping document (default="mappings/dataset.json")
        --sparql', sparql endpoint (default='http://deepcarbon.tw.rpi.edu:3030/VIVO/query')
        [out]: file name of the elasticsearch bulk ingest file

    e.g. `python3 ingest-datasets.py [out] --threads 4 --mapping mappings/dataset.json`


### Line command examples for the ingest process:

1. To start elastic search: `[elastic search folder]/bin/elasticsearch`

2. (CAUTION!) Delete existing data to avoid uploading error due to mismatching:
      * (For localhost) `curl -XDELETE 'localhost:9200/dco/dataset'`
      * (For dcotest)   `curl -XDELETE 'dcotest.tw.rpi.edu:49200/dco/dataset'`

3. Manually upload mapping:
      * (For localhost) `curl -XPUT 'localhost:9200/dco/dataset/_mapping?pretty' --data-binary @mappings/dataset.json`
      * (For dcotest)   `curl -XPUT 'dcotest.tw.rpi.edu:49200/dco/dataset/_mapping?pretty' --data-binary @mappings/dataset.json`
      * NOTE: The mapping for the person type includes a custom analyzer to better sort names with special characters. Install the required plugin and update the index settings before loading the mapping OR remove the name.sort field from person.json.

4. Generate bulk data:
    1. Just generate bulk data:
      * `python3 ingest-datasets-old-2.py output` and then upload bulk data manually
      * (For localhost) `curl -XPOST 'localhost:9200/_bulk' --data-binary @[out]`
      * (For dcotest)   `curl -XPOST 'dcotest.tw.rpi.edu:49200/_bulk' --data-binary @[out]`
    2. Generate bulk data and upload bulk data automatically:
      * (For localhost) `python3 ingest-datasets.py --es 'http://localhost:9200' --publish [out]`
      * (For dcotest)   `python3 ingest-datasets.py --es 'http://dcotest.tw.rpi.edu:49200' --publish [out]`

5. To view and operate in Sense:
      - GET dco/dataset/_mapping
      - GET dco/dataset/_search
      - DELETE /dco/dataset/
      - DELETE /dco/dataset/_mapping
      - and etc...
