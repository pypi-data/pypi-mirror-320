import numpy as np

def evaluate(model, X, y):
    """모델 성능 평가"""
    output = X
    for layer in model.layers:
        output = layer.forward(output)
    
    pred = np.argmax(output, axis=1)
    true = np.argmax(y, axis=1)
    accuracy = np.mean(pred == true)
    return accuracy

def categorical_accuracy(y_true, y_pred):
    """범주형 정확도 계산"""
    return np.mean(np.argmax(y_true, axis=1) == np.argmax(y_pred, axis=1))
