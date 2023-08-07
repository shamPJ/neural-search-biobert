import glob
import h5py
import numpy as np
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import time

def get_local_data():
    print("Fetching data from local DB (csv file with articles info) ...")
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(dfs)
    return df

def extract_embs():
    print("Fetching saved embeddings ...")
    h5_files = glob.glob(os.path.join("data", "*.h5"))
    
    # save PMIDs and embs in lists
    ids = []
    embs = []
    
    for file in h5_files:
        file = h5py.File(file, 'r')
        embs_group = file['embs_group']
        embs_group_keys = embs_group.keys()
        for key in embs_group_keys:
            if key not in ids:
                ids.append(int(key))
                embs.append(embs_group[key][:])
        print(file.keys())
    
    return ids, embs

def cosine_sim(emb1, emb2):
    return (np.dot(emb1, emb2.reshape(-1,1)) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

def compute_similarity(query, emb_abstract, model):
    emb_query = model.encode(query)
    # cosine similarity between query and each sentence in a corpus
    similarity_score = cosine_sim(emb_query, emb_abstract)
    return similarity_score[0]

def sort_by_similarity(query):
    """
    Input: query - string
    Output: list of dicts
    """
    # retrieve PMIDs and embeddings from saved .h5 files 
    ids, embs = extract_embs()
    # retrieve PMIDs from saved csv file ("database")
    df =  get_local_data()

    # MODEL
    print("Uploading model ...")
    model = SentenceTransformer('pritamdeka/S-BioBert-snli-multinli-stsb')
    
    articles = []
    scores = []
    print("Computing similarity score ...")
    for PMID, emb_abstract in zip(ids, embs):
        title, abstract = df[df["PMID"]==PMID]["Title"].values[0], df[df["PMID"]==PMID]["Abstract"].values[0]
        similarity_score = compute_similarity(query, emb_abstract, model)
        articles.append( (title, abstract) )
        scores.append(similarity_score)
    print("Done.")
    
    # sort by similarity score
    ind = np.argsort(-np.array(scores))
    sorted_articles = []

    # return 20 first relevant articles
    for i in ind[:10]:
        sorted_articles.append({
            'PMID': ids[i],
            'Title': articles[i][0],
            'Abstract': articles[i][1][:1000] + '...',
            'Similarity': scores[i]
        })

    return sorted_articles

