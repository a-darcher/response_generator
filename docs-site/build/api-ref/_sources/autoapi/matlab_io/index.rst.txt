matlab_io
=========

.. py:module:: matlab_io

.. autoapi-nested-parse::

   matlab.io
   =========

   Helper functions for making pandas DataFrames Matlab-interpretable.

   Use:
   ----
   ...
   dataset = pd.concat((df_nc, df_c))
   dataset_randomized = dataset.sample(frac=1, random_state=rng.integers(1e9)).reset_index(drop=True)

   mat_dict = {col: dataset_randomized[col].to_numpy() for col in dataset_randomized.columns}

   cell_cols = ["rasters", "supp_rasters"]  # adjust as needed
   matdict = force_cells_for_columns(dataset_randomized, cell_cols)

   savemat(path_save / f"{datetime.today().strftime('%Y-%m-%d')}_{int(n_samples)}_simulated_responses.mat", mat_dict)



Functions
---------

.. autoapisummary::

   matlab_io.normalize_trials
   matlab_io.inner_cell_row
   matlab_io.force_cells_for_columns


Module Contents
---------------

.. py:function:: normalize_trials(x)

   Force common trial format.

   :param x: set of trials
   :type x: list-like

   :returns: np.array of trials shaped to have at least one dimension
   :rtype: np.array


.. py:function:: inner_cell_row(trials)

   Forces trials to have cell-like format.

   :param trials: at least 1D numpy array
   :type trials: np.array

   :returns: 1xK array, where each element along the array is a trial
   :rtype: np.array


.. py:function:: force_cells_for_columns(df, cell_cols)

   Format an existing DataFrame to a Matlab-friendly format.

   :param df: simulated data
   :type df: pd.DataFrame
   :param cell_cols: columns to be reformatted
   :type cell_cols: list of strings

   :returns: DataFrame with data columns modified to maintain cell structure when imported to Matlab
   :rtype: pd.DataFrame


