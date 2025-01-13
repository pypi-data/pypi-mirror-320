import numpy as np

def to_categorical(y, num_classes=None):
    """레이블을 원-핫 인코딩으로 변환"""
    y = np.array(y, dtype='int')
    input_shape = y.shape
    
    # Flatten
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes))
    categorical[np.arange(n), y] = 1
    
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    
    return categorical

def train_test_split(X, y, test_size=0.2, shuffle=True):
    """데이터를 학습/테스트 세트로 분할"""
    if shuffle:
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
    
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    return X_train, X_test, y_train, y_test

def evaluate(model, X, y):
    """모델 평가"""
    output = model.predict(X)
    if len(y.shape) > 1:  # 원-핫 인코딩된 레이블
        return np.mean(np.argmax(output, axis=1) == np.argmax(y, axis=1))
    return np.mean(np.argmax(output, axis=1) == y) 