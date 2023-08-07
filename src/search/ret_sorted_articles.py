import numpy as np
from pubmed_query import get_abstract, get_PMIDs
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import time

def cosine_sim(emb1, emb2):
    return (np.dot(emb1, emb2.reshape(-1,1)) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

def compute_similarity(query, abstract, model):
    
    # split long text into the list of sentences
    corpus = abstract[:-1].split(".")
    emb_query = model.encode(query)
    embs_corpus = model.encode(corpus) 
    # cosine similarity between query and each sentence in a corpus
    similarity_score = np.mean([ cosine_sim(emb_query, emb) for emb in embs_corpus ])
    print(similarity_score)
    return similarity_score

def sort_by_similarity(query):
    """
    Input: query - string
    Output: list of dicts
    """
    # retrieve PMIDs from pubmed
    PMIDs = get_PMIDs(query)

    # MODEL
    print("Uploading model ...")
    model = SentenceTransformer('pritamdeka/S-BioBert-snli-multinli-stsb')
    
    articles = []
    scores = []
    print("Computing similarity score ...")
    for PMID in PMIDs:
        title, abstract = get_abstract(PMID)
        similarity_score = compute_similarity(query, abstract, model)

        articles.append( (title, abstract) )
        scores.append(similarity_score)
    print("Done.")
    
    # sort by similarity score
    ind = np.argsort(-np.array(scores))
    sorted_articles = []

    for i in ind:
        sorted_articles.append({
            'PMID': PMIDs[i],
            'Title': articles[i][0],
            'Abstract': articles[i][1][:1000] + '...',
            'Similarity': scores[i]
        })

    return sorted_articles

