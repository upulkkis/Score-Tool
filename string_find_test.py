import re
from fuzzywuzzy import process
from scipy.spatial import procrustes
import numpy as np
import pickle

with open('./database/no_data_orchestra.pickle', 'rb') as handle:
    orchestra = pickle.load(handle)

def test():
    tu=23
    pe='sdf'
    return tu, pe
#print(list(orchestra.keys()))
instruments=list(orchestra.keys())
#instruments=['violin', 'cello', 'tenor_trombone', 'flute']
name='vcl'

a=np.array([[0, 0],[1, 60],[2, 30],[3, 50],[4, 20],[5, -20],[6, -60]])
b=np.array([[0, 0],[1, -60],[2, -30],[3, -50],[4, -20],[5, 20],[6, 60]])
#b=np.array([[0, 0],[1, 6],[2, 3],[3, 5],[4, 2],[5, -2], [6, -6]])

g, h = test()
#indices = [i for i, s in enumerate(instruments) if name in s]

#print(instruments[indices[0]])
#print(re.search(name, r"(?=("+'|'.join(instruments)+r"))"))

print(process.extractOne(name, instruments))

mtx1, mtx2, disparity = procrustes(a, b)
#print(mtx1)
#print(mtx2)
print(disparity)