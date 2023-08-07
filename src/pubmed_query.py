from bs4 import BeautifulSoup
import click
import csv
import json
import math
import os
import requests
from tqdm import tqdm
import time
from time import sleep

# Code modified from: 
# https://techoverflow.net/2022/01/01/how-to-search-pubmed-entrez-api-with-python-and-filter-results-by-metadata/

# E-utilities Pubmed https://dataguide.nlm.nih.gov/eutilities/how_eutilities_works.html
# The E-utilities In-Depth: Parameters, Syntax and More https://www.ncbi.nlm.nih.gov/books/NBK25499/

db = 'pubmed'
domain = 'https://www.ncbi.nlm.nih.gov/entrez/eutils'

def xml_to_txt(xml_file):
    """
    Function to parse xml file and extract article's abstract, mesh and keywords.
    :param xml_file: xml file retrieved from pubmed
    :output: lists abstract, mesh, keywords
    """
    soup = BeautifulSoup(xml_file, 'xml')
    abstract_list_xml = soup.find_all('AbstractText')
    mesh_xml = soup.find_all('MeshHeading')
    keywords_xml = soup.find_all('Keyword')

    if (len(abstract_list_xml) != 0):
        abstract_list_txt = [abstr.text for abstr in abstract_list_xml]
        abstract = " ".join(abstract_list_txt)
        abstract = abstract.replace(u'\xa0', u' ')

        mesh = [term.text for term in mesh_xml]
        keywords = [term.text for term in keywords_xml]

        return abstract, mesh, keywords
    else:
        abstract = None
        return abstract, [], []

  
# annotate starter function cli() with @click.group indicating that this will be a group of commands
@click.group()
def cli():
    pass

@cli.command(name='esearch')
@click.argument('query')
@click.option('--nresults', '-n', default=50000, help='Number of results to return for esearch', show_default=True)
@click.option('--narticles', '-a', default=200, help='Number of results to return for esummary', show_default=True)
@click.option('--retmode', '-m', default='json', help='Return format for esearch', show_default=True)

def esearch(query, nresults, narticles, retmode):

    '''
    Takes as input arg query (string) and options to send requests to Pubmed database.
    Eutils used to retrieve data:
    - esearch returns list of articles PMIDs returned by pubmed for a user query
    - esummary returns metadata (we save only pubtype) for a given PMID
    - efetch returns abstarct for a given PMID
    Function returns csv file with article PMID and abstract, if exist pubtype, keywords, mesh terms.
    '''

    # file name to store esearch results
    search_res = "data" + os.sep + query + "_esearch.json"
    # check if file exist
    is_file = os.path.isfile(search_res)
    if is_file == False:
        # standard query
        # esearch: retmax - maximum of 100,000 records. To retrieve more than 100,000 UIDs, submit multiple esearch requests while incrementing the value of retstart 
        # https://www.ncbi.nlm.nih.gov/books/NBK25499/?utm_source=blog&utm_medium=referral&utm_campaign=pubmed-api&utm_term=post1&utm_content=20210929link3#chapter4.ESearch
        queryLinkSearch = f'{domain}/esearch.fcgi?db={db}&sort=relevance&retmax={nresults}&retmode={retmode}&term={query}'
        queryLinkSearch = queryLinkSearch + " AND English[Language]"
        response = requests.get(queryLinkSearch)
        pubmedJson = response.json()
        # save results as json file
        with open(search_res, 'w') as f:
            json.dump(pubmedJson, f)
    else:
        print("Loading existing esearch file ...")
        with open(search_res) as f:
            pubmedJson_str = f.read()
        pubmedJson = json.loads(pubmedJson_str)

    PMID = []
    Type = []
    Title = []
    Abstract = []
    Keywords = []
    MeSH = []

    # n.o. trials when error is returned (see the error message at the end)
    num_tries = 5
    # request summary in batch
    batch_size = 100
    iters = int(math.ceil(len(pubmedJson["esearchresult"]["idlist"])/batch_size))

    for i in range(iters):
        # collect ~n_articles 
        if len(PMID)< narticles:
            # select batch of PMIDs
            items = pubmedJson["esearchresult"]["idlist"][i*batch_size: i*batch_size+batch_size]
            # ugly hack - dummy PMID=0, to avoid 'error': 'Invalid uid [XXX at position= 0'..]
            items = [0] + items
            # convert PMID str to int
            items = [int(item) for item in items]
            
            for try_ in range(num_tries):
                    try:
                        queryLinkSummary = f'{domain}/esummary.fcgi?db={db}&id={items}&retmode=json'
                        metadata = requests.get(queryLinkSummary).json()
                        ids = metadata['result']['uids']
                        sleep(0.4)
                    except:
                        print(f'Failed to fetch esummary for the batch {i}, but we can try {num_tries - try_ - 1} more time(s)')
                        sleep(60)
                    else:
                        print(f'Fetched batch {i} esummary successfully')
                        for paperId in tqdm(ids):
                            title = metadata['result'][paperId]['title']
                            try:
                                pubtype = metadata['result'][paperId]['pubtype']
                                pubtype = pubtype[-1]
                            except:
                                pubtype = 'None'
                            # fetch abstract
                            for try_ in range(num_tries):
                                try:
                                    queryLinkXML = f'{domain}/efetch.fcgi?db={db}&id={paperId}&retmode=xml&rettype=abstract'
                                    xml_file = requests.get(queryLinkXML).text
                                    sleep(0.4)
                                except:
                                    print(f'Failed to query efetch for the PMID {paperId}, but we can try {num_tries - try_ - 1} more time(s)')
                                    sleep(60)
                                else:
                                    abstract, mesh, keywords = xml_to_txt(xml_file)

                                    if (abstract != None):
                                        PMID.append(paperId)
                                        Title.append(title)
                                        Abstract.append(abstract)
                                        Keywords.append(keywords)
                                        MeSH.append(mesh)
                                        Type.append(pubtype)

                                        break
                        break
    
    rows = zip(PMID, Title, Abstract, MeSH, Keywords, Type)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_name = "data" + os.sep + query + '_' + timestr + ".csv"
    with open(file_name, "w") as f:
        writer = csv.writer(f)
        writer.writerow(['PMID', 'Title', 'Abstract', 'MeSH', 'Keywords', 'Type'])
        for row in rows:
            writer.writerow(row)

'''
If run without try-except-else and sleep delay often retruns connection error.
Error returned:

requests.exceptions.ConnectionError: HTTPSConnectionPool(host='www.ncbi.nlm.nih.gov', port=443): 
Max retries exceeded with url: /entrez/eutils/efetch.fcgi?db=pubmed&id=36269052&retmode=xml&rettype=abstract 
(Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7ff0313f6ca0>: 
Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
'''
        
if __name__=="__main__":
    cli()