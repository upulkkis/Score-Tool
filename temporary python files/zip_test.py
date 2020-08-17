import bz2
import pickle

with open('orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)

#with gzip.GzipFile('orchestra.pgz', 'w') as f:
#    pickle.dump(orchestra, f)

with bz2.BZ2File('orchestra.pbz2', 'w') as f:
    pickle.dump(orchestra, f)

def load_zipped_pickle(filename):
    with gzip.open(filename, 'rb') as f:
        loaded_object = cPickle.load(f)
        return loaded_object