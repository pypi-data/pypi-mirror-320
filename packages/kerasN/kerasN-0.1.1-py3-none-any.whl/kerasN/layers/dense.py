import numpy as np
from .base import Layer
from ..activations import get_activation

class Dense(Layer):
    def __init__(self, units, activation=None):
        super().__init__()
        self.weights = None
        self.bias = None
        self.units = units
        self.activation_name = activation
        self.activation_fn, self.activation_derivative = get_activation(activation)
        
    def build(self, input_shape):
        """레이어 초기화"""
        self.input_shape = input_shape  # 입력 shape 저장
        n_inputs = int(np.prod(input_shape[1:]))
        
        # Xavier/Glorot 초기화
        if self.weights is None:
            limit = np.sqrt(6 / (n_inputs + self.units))
            self.weights = np.random.uniform(-limit, limit, (n_inputs, self.units))
        if self.bias is None:
            self.bias = np.zeros(self.units)
        
        # 출력 shape 계산
        self.output_shape = (input_shape[0], self.units)
        
    def forward(self, input):
        self.input = input
        # 입력 reshape
        self.flattened = input.reshape(len(input), -1)
        # 선형 변환
        self.linear_output = np.dot(self.flattened, self.weights) + self.bias
        # 활성화 함수
        self.output = self.activation_fn(self.linear_output)
        return self.output
        
    def backward(self, grad, learning_rate):
        if self.activation_name != 'softmax':  # softmax는 이미 gradient에 반영됨
            grad = grad * self.activation_derivative(self.linear_output)
            
        # 가중치 그래디언트
        weights_grad = np.dot(self.flattened.T, grad)
        bias_grad = np.sum(grad, axis=0)
        
        # 입력 그래디언트
        input_grad = np.dot(grad, self.weights.T)
        input_grad = input_grad.reshape(self.input.shape)
        
        # 파라미터 업데이트
        self.weights -= learning_rate * weights_grad
        self.bias -= learning_rate * bias_grad
        
        return input_grad

    def compute_output_shape(self):
        """출력 shape 계산"""
        if not hasattr(self, 'input_shape'):
            return None
        return (self.input_shape[0], self.units)

    def count_params(self):
        """파라미터 수 계산"""
        if not hasattr(self, 'input_shape'):
            return 0
        n_inputs = np.prod(self.input_shape[1:])
        return n_inputs * self.units + self.units  # weights + bias