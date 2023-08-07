import os

# run file to collect data for "custom DB":
#
# - send query to pubmed with E-utilities 
# - parse text, compute embs
# - save all processed/ computed data
#  In this toy example "custom DB" is just a csv file

dir_path = os.path.join( "src", "data_retrieval")

os.system("python " + os.path.join(dir_path, 'pubmed_query.py') + " esearch -a 50 'burnout prevention stress mood mental health' ")
os.system("python " + os.path.join(dir_path, 'compute_embeddings.py'))
