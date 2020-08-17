import numpy as np

def assign_dynamics (dyn, inst, dyn_list):
    idx = np.where(dyn_list[0][:] == inst)  # Find the index of item in dynamics

    # Get the mesured sound pressure level from dynamics file
    if dyn == 'p':
        dyn_db = dyn_list[1][idx[0][0]]
    elif dyn == 'mf':
        dyn_db = dyn_list[2][idx[0][0]]
    elif dyn == 'f':
        dyn_db = dyn_list[3][idx[0][0]]
    else:
        dyn_db = 60

    return dyn_db