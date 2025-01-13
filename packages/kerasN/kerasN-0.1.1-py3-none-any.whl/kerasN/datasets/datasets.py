import numpy as np
from sklearn.datasets import load_digits, load_iris, load_breast_cancer, load_wine
import os
import sys

def load_data(name, normalize=True, reshape_to_image=False):
    """
    데이터셋을 로드합니다.
    
    Parameters
    ----------
    name : str
        데이터셋 이름
        - 기본 데이터셋: 'iris', 'digits', 'breast_cancer', 'wine'
        - 이미지 데이터셋: 'mnist', 'fashion_mnist', 'cifar10'
    normalize : bool
        데이터 정규화 여부 (기본값: True)
    reshape_to_image : bool
        이미지 형태로 reshape 할지 여부 (기본값: False)
        
    Returns
    -------
    tuple
        (X, y) - 입력 데이터와 레이블
    """
    
    # Pyodide 환경 체크
    is_pyodide = 'pyodide' in sys.modules
    
    if is_pyodide:
        from .pyodide_datasets import load_pyodide_dataset
        return load_pyodide_dataset(name, normalize, reshape_to_image)
        
    # 기본 sklearn 데이터셋
    sklearn_datasets = {
        'iris': load_iris,
        'digits': load_digits,
        'breast_cancer': load_breast_cancer,
        'wine': load_wine
    }
    
    if name in sklearn_datasets:
        data = sklearn_datasets[name]()
        X, y = data.data, data.target
        
        if normalize:
            X = X / np.max(X)
            
        if reshape_to_image and name == 'digits':
            X = X.reshape(-1, 8, 8, 1)
            
        return X, y
        
    # 대규모 이미지 데이터셋
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    if name in ['mnist', 'fashion_mnist', 'cifar10']:
        data_path = os.path.join(data_dir, f'{name}_data.npy')
        if not os.path.exists(data_path):
            from .download_datasets import download_and_save_dataset
            X, y = download_and_save_dataset(name)
        else:
            X = np.load(os.path.join(data_dir, f'{name}_data.npy'))
            y = np.load(os.path.join(data_dir, f'{name}_target.npy'))
            
        if normalize:
            X = X.astype('float32') / 255.0
            
        if reshape_to_image:
            if name in ['mnist', 'fashion_mnist']:
                X = X.reshape(-1, 28, 28, 1)
            elif name == 'cifar10':
                X = X.reshape(-1, 32, 32, 3)
                
        return X, y
        
    raise ValueError(f"Unknown dataset: {name}") 