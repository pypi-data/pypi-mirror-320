import pandas as pd
import numpy as np
import scipy.io
import json
import os
from sklearn import datasets
class DataReader:
    """
    DataReader: A class for reading datasets from various formats and loading sklearn datasets.
    """

    def __init__(self, file=None, make=False):
        """
        Initialize the DataReader.

        Parameters
        ----------
        file : str
            Path to the file to read.
        make : bool, optional (default=False)
            If True, generates synthetic datasets using scikit-learn.
        """
        self.file = file # Path to the input file
        self.make_ = make # Whether to generate synthetic datasets
        self.format = None # File format, determined by `_detect_format` method

        # Detect the file format if a file path is provided
        if file:
            self.format = self._detect_format(file=file)
    
    def _detect_format(self, file):
        """
        Detect the file format based on its extension.

        Parameters
        ----------
        file : str
            The file path.
        
        Returns
        -------
        format : str
            The file extension in lowercase.

        Raises
        ------
        ValueError: 
            If the file does not have an extension.
        """
        
        if '.' not in file:
            raise ValueError(f"File `{file}` does not have a valid extension.")
        
        return file.split('.')[-1].lower()
    
    def read_csv(self, *args, **kwargs):
        """
        Read CSV files.

        Parameters
        ----------
        *args : 
            Positional arguments to pass to pandas.read_csv.
        **kwargs : 
            Keyword arguments to pass to pandas.read_csv.

        Returns
        -------
        pandas.DataFrame:
            The laoded CSV file as a DataFrame.

        Raises
        ------
        FileNotFoundError : 
            If the specified file is not found.
        ValueError : 
            If the file is not a value CSV file.
        """
        try:
            # Attempt to read the CSV file
            return pd.read_csv(self.file, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{self.file}` not found.")
        except pd.errors.EmptyDataError:
            raise ValueError(f"File `{self.file}` is empty or not a valid CSV.")

    def read_json(self, as_dataframe=False, *args, **kwargs):
        """
        Read JSON files.

        Parameters
        ----------
        as_dataframe : bool, optional (default=False)
            If True, converts JSON data to a pandas DataFrame.
        *args : 
            Positional argumetns for pandas.read_json(if as_dataframe=True).
        **kwargs : 
            Keyword arguments for pandas.read_json(if as_dataframe=True).

        Returns
        -------
         dict or pandas.DataFrame : 
            The loaded JSON data

        Raises
        ------
        FileNotFoundError : 
            If the file does not exist.
        ValueError : 
            If the file is not a valid JSON format.
        """
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
            
            # Convert to DataFrame if requested
            if as_dataframe:
                return pd.json_normalize(data, *args, **kwargs)
            
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{self.file}` not found.")
        except json.JSONDecodeError:
            raise ValueError(f"File `{self.file}` is not a valid JSON format.")
    
    def read_xlsx(self, sheet_name=0, *args, **kwargs):
        """ 
        Read Excel files.

        Parameters
        ----------
        sheet_name : int, str, list or None (default=0)
            The sheet name(s) to read. Defaults to the first sheet (0)
        *args : 
            Positional arguments for pandas.read_excel.
        **kwargs : 
            Keyword arguments for panda.read_excel.

        Returns
        -------
        pandas.DataFrame or dict : 
            The loaded Excel data as a DataFrame or a dictionary of DataFrames (if multiple sheets).

        Raises
        ------
        FileNotFoundError : 
            If the file does not exist.
        ValueError : 
            If the file is not a valid Excel format.
        """
        
        try:
            return pd.read_excel(self.file, sheet_name=sheet_name, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{self.file}` not found.")
        except ValueError as e:
            raise ValueError(f"File `{self.file}` is not a valid Excel file: {e}")
    
    def read_mat(self, variable_names=None, *args, **kwargs):
        """
        Read MATLAB .mat files.

        Parameters
        ----------
        variable_names : list or None
            A list of variable names to extract. If None, all variables are loaded.

        Returns
        -------
        dict : 
            A dictionary containing variables from the `.mat` file.

        Raises
        ------
        FileNotFoundError : 
            If the file does not exist.
        ValueError : 
            If the file is not a valid `.mat` file.
        """
        try:
            return scipy.io.loadmat(self.file, variable_names=variable_names, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{self.file}` not found.")
        except Exception as e:
            raise ValueError(f"File `{self.file}` could not be loaded as a valid `.mat` file.")
    
    def read_parquet(self, engine='auto', *args, **kwargs):
        """
        Read Parquet files.

        Parameters
        ----------
        engine : str (default='auto')
            Parquet engine to use. Options include 'pyarrow', 'fastparquet' or 'auto'
        *args : 
            Positional arguments for pandas.read_parquet.
        **kwargs : 
            Keyword arguments for pandas.read_parquet.

        Returns
        -------
        pandas.DataFrame : 
            The loaded Parquet data as a DataFrame.

        Raises
        ------
        FileNotFoundError : 
            If the file does not exist.
        ValueError : 
            If the file is not a valid Parquet file.
        """
        try : 
            return pd.read_parquet(self.file, engine=engine, *args, **kwargs)
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{self.file}` not found.")
        except ValueError as e:
            raise ValueError(f"File `{self.file}` could not be loaded as a valid Parquet file: {e}")

    def make(self, dataset_name='classification', *args, **kwargs):
        """
        Generate synthetic datasets using scikit-learn.

        Parameters
        ----------
        dataset_name : str (default='classification')
            The type of synthetic dataset to create. Include 'classification', 'regression', 'blobs',  etc.
        *args : 
            Positional arguments for the scikit-learn dataset function.
        **kwargs : 
            Keyword arguments for the scikit-learn dataset function.

        Returns
        -------
        tuple : 
            A tuple of generated data(e.g., (X,y))

        Raises:
        ValueError : 
            If the specified dataset name is not supported.
        """
        try : 
            method_name = f"make_{dataset_name}"
            if hasattr(datasets, method_name):
                return getattr(datasets, method_name)(*args, **kwargs)
            else:
                raise ValueError(f"Dataset generation method `{method_name}` is not availabel in sklearn.datasets.")
        except Exception as e:
            raise ValueError(f"Error generating synthetic dataset: {e}")
    
    def load(self, dataset_name, *args, **kwargs):
        """
        Load or fetch pre-defined sklearn datasets.

        Parameters
        ----------
        dataset_name : str
            The name of the dataset to load or fetch.
            Examples: 'iris', 'digits', 'fetch_openml', etc.
        *args : 
            Positional arguments for the specified dataset function.
        **kwargs : 
            Keyword arguments for the specified dataset function.
        
        Returns
        -------
        Various types : The loaded of fetched dataset, depending on the function.

        Raises
        ------
        ValueError : 
            If the dataset name is not recognized or not supported.
        """
        try:
            # Determine if it's a `load_` or `fetch_` method
            if hasattr(datasets, f"load_{dataset_name}"):
                method_name = f"load_{dataset_name}"
            elif hasattr(datasets, f"fetch_{dataset_name}"):
                method_name = f"fetch_{dataset_name}"
            else:
                raise ValueError(f"Dataset `{dataset_name}` is not available in scikit-learn.")
            
            # Call the appropriate method
            return getattr(datasets, method_name)(*args, **kwargs)
        except Exception as e:
            raise ValueError(f"Error loading or fetchin dataset `{dataset_name}`: {e}")

    def __call__(self, *args, **kwargs):
        """
        Automatically determine the correct method to read the dataset
        based on the file format or generation flag.

        Parameters
        ----------
        *args : 
            Positional arguments for the target method.
        **kwargs : 
            Keyword arguments for the target method.

        Returns
        -------
        Various type : 
            The result of the invoked method.

        Raises
        ------
        NotImplementedError : 
            If no suitable method is found for the file format.
        """

        if self.make_:
            return self.make(*args, **kwargs)
        if not self.format:
            raise ValueError("File format could not be detected. Please specify a valid file.")
        
        method_name = f"read_{self.format}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(*args, **kwargs)
        raise NotImplementedError(f"Reading files with format `{self.format}` is not supported.")
        