from .base import Layer
import numpy as np

class Flatten(Layer):
    def forward(self, input):
        self.input_shape = input.shape
        return input.reshape(len(input), -1)
        
    def backward(self, grad, learning_rate):
        return grad.reshape(self.input_shape)

    def compute_output_shape(self):
        """출력 shape 계산"""
        if not hasattr(self, 'input_shape'):
            return None
        return (self.input_shape[0], np.prod(self.input_shape[1:]))

    def count_params(self):
        """파라미터 수 계산"""
        return 0  # Flatten 레이어는 학습 파라미터가 없음