import numpy as np

def relu(x):
    """ReLU 활성화 함수"""
    return np.maximum(0, x)

def relu_derivative(x):
    """ReLU 도함수"""
    return np.where(x > 0, 1, 0)

def sigmoid(x):
    """시그모이드 활성화 함수"""
    return 1 / (1 + np.exp(-np.clip(x, -100, 100)))  # 수치 안정성을 위한 클리핑

def sigmoid_derivative(x):
    """시그모이드 도함수"""
    s = sigmoid(x)
    return s * (1 - s)

def tanh(x):
    """하이퍼볼릭 탄젠트 활성화 함수"""
    return np.tanh(x)

def tanh_derivative(x):
    """하이퍼볼릭 탄젠트 도함수"""
    return 1 - np.tanh(x) ** 2

def softmax(x):
    """소프트맥스 활성화 함수"""
    exp_x = np.exp(x - np.max(x, axis=-1, keepdims=True))  # 수치 안정성을 위한 최대값 빼기
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)

def softmax_derivative(x):
    """소프트맥스 도함수 (크로스 엔트로피 손실과 함께 사용될 때)"""
    s = softmax(x)
    return s * (1 - s)  # 단순화된 버전

def leaky_relu(x, alpha=0.01):
    """Leaky ReLU 활성화 함수"""
    return np.where(x > 0, x, alpha * x)

def leaky_relu_derivative(x, alpha=0.01):
    """Leaky ReLU 도함수"""
    return np.where(x > 0, 1, alpha)

# 활성화 함수와 도함수를 매핑하는 딕셔너리
ACTIVATIONS = {
    'relu': (relu, relu_derivative),
    'sigmoid': (sigmoid, sigmoid_derivative),
    'tanh': (tanh, tanh_derivative),
    'softmax': (softmax, softmax_derivative),
    'leaky_relu': (leaky_relu, leaky_relu_derivative),
    None: (lambda x: x, lambda x: 1)  # 선형(항등) 활성화 함수
}

def get_activation(name):
    """활성화 함수와 도함수 반환"""
    if name not in ACTIVATIONS:
        raise ValueError(f'Unknown activation function: {name}')
    return ACTIVATIONS[name]