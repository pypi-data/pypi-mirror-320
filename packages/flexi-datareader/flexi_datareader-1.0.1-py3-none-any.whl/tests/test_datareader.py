import pytest
import pandas as pd
import json
import numpy as np
from model.datareader import DataReader

@pytest.fixture
def csv_file(tmp_path):
    """Create a temporary CSV file for testing."""
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({'col1':[1, 2, 3], 'col2':['a', 'b', 'c']})
    df.to_csv(file_path, index=False)
    return str(file_path)

@pytest.fixture
def json_file(tmp_path):
    """Create a temporary JSON file for testing."""
    file_path = tmp_path / "test.json"
    data      = {'key1': 'value1', 'key2': [1, 2, 3]}
    with open(file_path, 'w') as f:
        json.dump(data, f)
    return str(file_path)

@pytest.fixture
def excel_file(tmp_path):
    """Create a temporary Excel file for testing."""
    file_path = tmp_path / "test.xlsx"
    df        = pd.DataFrame({'col1':[1, 2, 3], 'col2':['a', 'b', 'c']})
    df.to_excel(file_path, index=False)
    return str(file_path)

def test_read_csv(csv_file):
    """Test reading CSV file."""
    reader = DataReader(file=csv_file)
    data   = reader()

    assert isinstance(data, pd.DataFrame), 'CSV file not read as a DataFrame.'
    assert data.shape == (3, 2), f"CSV file shape is incorrect: {data.shape}"

def test_read_json(json_file):
    """Test reading a JSON file."""
    reader = DataReader(file=json_file)
    data   = reader()

    assert isinstance(data, dict), 'JSON file not read as a dictionary.'
    assert data['key1'] == 'value1', "JSON key `key1` does not have the expected value."
    assert data['key2'] == [1, 2, 3], "JSON key `key2` does not have the expected list." 

def test_read_excel(excel_file):
    """Test reading Excel file."""
    reader = DataReader(file=excel_file)
    data   = reader()

    assert isinstance(data, pd.DataFrame), 'Excel file not read as a DataFrame.'
    assert data.shape == (3, 2), f"Excel file shape is incorrect: {data.shape}"

def test_read_invalid_file():
    """Test handling unsupported file formats."""
    reader = DataReader(file='nonexistent.csv')
    with pytest.raises(FileNotFoundError):
        reader()
    
def test_generate_synthetic_dataset():
    """Test generating a synthetic dataset."""
    reader = DataReader(make=True)
    X, y   = reader(dataset_name='classification', n_samples=100, n_features=5,
                    n_classes=2)
    
    assert isinstance(X, np.ndarray), "Generated features (X) are not a numpy array."
    assert isinstance(y, np.ndarray), "Generated labels (y) are not a numpy array."
    assert X.shape == (100, 5), f"Generated features shape is incorrect: {X.shape}"
    assert len(y)  == 100, f"Generated labels length is incorrect: {len(y)}"

def test_load_sklearn_dataset():
    """Test loading a pre-defined sklearn datasets."""
    reader = DataReader()
    iris   = reader.load('iris')

    assert 'data' in iris, "Loaded dataset does not contain `data` attribute."
    assert 'target' in iris, "Loaded dataset does not contain `target` attribute."
    assert iris.data.shape == (150, 4), f"Loaded dataset `data` shape is incorrect: {iris.data.shape}"