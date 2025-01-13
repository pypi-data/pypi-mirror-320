import os
import numpy as np
import pandas as pd

def load_csv(filepath):
    """CSV 파일 로드"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return pd.read_csv(filepath)

def load_npy(filepath):
    """NPY 파일 로드"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    return np.load(filepath) 