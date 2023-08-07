import os

# run file to collect data for "custom DB":
#
# - send query to pubmed with E-utilities 
# - parse text, compute embs
# - save all processed/ computed data (articles info saved as csv file and embeddings as .h5 group)
#  In this toy example "custom DB" is just a csv file

os.system("python " + os.path.join("src", 'pubmed_query.py') + " esearch -a 50 'burnout prevention stress mood mental health' ")
os.system("python " + os.path.join("src", 'compute_embeddings.py'))
