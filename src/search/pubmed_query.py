from bs4 import BeautifulSoup
import requests

db = 'pubmed'
domain = 'https://www.ncbi.nlm.nih.gov/entrez/eutils'
# esearch: retmax - maximum of 100,000 records. 
# To retrieve more than 100,000 UIDs, submit multiple esearch requests while incrementing the value of retstart 
retmax = 5

def get_PMIDs(query):
    queryLinkSearch = f'{domain}/esearch.fcgi?db={db}&retmax={retmax}&retmode=json&term={query}'
    response = requests.get(queryLinkSearch)
    pubmedJson = response.json()
    # return list of PMID values
    return pubmedJson['esearchresult']['idlist']

def get_txt(list_xml):
    list_txt = [el.text for el in list_xml]
    txt = " ".join(list_txt)
    txt = txt.replace(u'\xa0', u' ')
    return txt

def get_abstract(PMID):
    queryLinkXML = f'{domain}/efetch.fcgi?db={db}&id={PMID}&retmode=xml&rettype=abstract'
    xml_file = requests.get(queryLinkXML).text

    soup = BeautifulSoup(xml_file, 'xml')
    abstract_list_xml = soup.find_all('AbstractText')
    title_list_xml = soup.find_all('ArticleTitle')

    if (len(abstract_list_xml) != 0):
        abstract = get_txt(abstract_list_xml)
        title = get_txt(title_list_xml)
        return title, abstract
    else:
        return "", "No abstarct returned."     

                        