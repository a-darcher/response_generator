import numpy as np
from scipy.io import savemat

def normalize_trials(x):
    """Force common trial format.

    Args:
        x (list-like): set of trials

    Returns:
        np.array: np.array of trials shaped to have at least one dimension
    """
    if x is None:
        return []
    if isinstance(x, (list, tuple)):
        return [np.atleast_1d(np.asarray(t, float)) for t in x]
    if isinstance(x, np.ndarray):
        return [np.atleast_1d(x.astype(float))]

    return [np.atleast_1d(np.asarray(x, float))]

def inner_cell_row(trials):
    """Forces trials to have cell-like format. 

    Args:
        trials (np.array): at least 1D numpy array

    Returns:
        np.array: 1xK array, where each element along the array is a trial
    """
    K = max(1, len(trials))
    cell = np.empty((1, K), dtype=object)
    if len(trials) == 0:
        cell[0, 0] = np.array([], float)  
    else:
        for j, t in enumerate(trials):
            cell[0, j] = np.asarray(t, float)  
    return cell

def force_cells_for_columns(df, cell_cols):
    """Format an existing DataFrame to a Matlab-friendly format.

    Args:
        df (pd.DataFrame): simulated data
        cell_cols (list of strings): columns to be reformatted

    Returns:
        pd.DataFrame: DataFrame with data columns modified to maintain cell structure when imported to Matlab
    """
    out = {}
    n = len(df)

    for c in df.columns.difference(cell_cols):
        out[c] = df[c].to_numpy()

    for c in cell_cols:
        col = np.empty((n, 1), dtype=object)
        for i, x in enumerate(df[c].tolist()):
            trials = normalize_trials(x)
            col[i, 0] = inner_cell_row(trials)
        out[c] = col
    return out