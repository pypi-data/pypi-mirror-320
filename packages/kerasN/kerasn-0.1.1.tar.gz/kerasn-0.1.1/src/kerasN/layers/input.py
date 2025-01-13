import numpy as np
from .base import Layer

class Input(Layer):
    def __init__(self, shape):
        super().__init__()
        # 배치 차원을 제외한 입력 shape
        if isinstance(shape, int):
            self.shape = (shape,)
        else:
            self.shape = tuple(shape)
        self.input_shape = (None,) + self.shape
        
    def compute_output_shape(self):
        return self.input_shape
        
    def count_params(self):
        return 0
        
    def forward(self, input):
        return input
        
    def backward(self, grad, learning_rate):
        return grad 