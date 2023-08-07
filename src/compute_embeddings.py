import glob
import h5py
import numpy as np
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import time
from tqdm import tqdm

dir_path = os.path.join("data")

def get_local_data():
    print("Fetching data from local DB ...")
    csv_files = glob.glob(os.path.join("data", "*.csv"))
    dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(dfs)
    return df

def compute_embeddings():
    df = get_local_data()
    PMIDs = df['PMID']
    # split long text into the list of sentences
    corpus = df['Abstract'].apply(lambda x: x[:-1].split("."))

    print("Computing corpus embeddings ...")
    model = SentenceTransformer('pritamdeka/S-BioBert-snli-multinli-stsb')

    # save data in h5 file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    hf_path = os.path.join(dir_path, "emb_vectors_" + timestr + ".h5")
    hf = h5py.File(hf_path, "w")
    embs_group = hf.create_group('embs_group')

    for PMID, text in tqdm(zip(PMIDs, corpus)):
        embs = model.encode(text)                   # compute embs for each sentence
        embs = np.mean(embs, axis=0)                # compute mean embedding vector for abstract
        embs_group[str(PMID)] = np.asarray(embs)    # save data in h5 file
    hf.close()
    print("Done.")

compute_embeddings()   
  

                        