import numpy as np

def to_categorical(y, num_classes=None):
    """레이블을 원-핫 인코딩으로 변환"""
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes))
    categorical[np.arange(n), y] = 1
    return categorical

def train_test_split(X, y, test_size=0.2, shuffle=True):
    """데이터를 학습셋과 테스트셋으로 분할"""
    n_samples = len(X)
    n_test = int(n_samples * test_size)
    
    if shuffle:
        indices = np.random.permutation(n_samples)
        test_idx, train_idx = indices[:n_test], indices[n_test:]
    else:
        train_idx = np.arange(n_samples - n_test)
        test_idx = np.arange(n_samples - n_test, n_samples)
    
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
