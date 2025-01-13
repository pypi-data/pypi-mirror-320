import numpy as np
from .base import Layer

class MaxPool2D(Layer):
    def __init__(self, pool_size=2):
        super().__init__()
        self.pool_size = pool_size
        
    def forward(self, input):
        self.input = input
        batch_size, h, w, channels = input.shape
        new_h = h // self.pool_size
        new_w = w // self.pool_size
        
        self.output = np.zeros((batch_size, new_h, new_w, channels))
        self.mask = np.zeros_like(input)
        
        for i in range(new_h):
            for j in range(new_w):
                h_start = i * self.pool_size
                h_end = h_start + self.pool_size
                w_start = j * self.pool_size
                w_end = w_start + self.pool_size
                
                window = input[:, h_start:h_end, w_start:w_end, :]
                self.output[:, i, j, :] = np.max(window, axis=(1,2))
                
                # 마스크 생성
                window_reshaped = window.reshape(batch_size, -1, channels)
                max_idx = np.argmax(window_reshaped, axis=1)
                
                for b in range(batch_size):
                    for c in range(channels):
                        idx = max_idx[b, c]
                        h_idx = idx // self.pool_size
                        w_idx = idx % self.pool_size
                        self.mask[b, h_start+h_idx, w_start+w_idx, c] = 1
                        
        return self.output
        
    def backward(self, grad, learning_rate):
        grad_input = np.zeros_like(self.input)
        batch_size, h, w, channels = grad.shape
        
        for i in range(h):
            for j in range(w):
                h_start = i * self.pool_size
                h_end = h_start + self.pool_size
                w_start = j * self.pool_size
                w_end = w_start + self.pool_size
                
                grad_input[:, h_start:h_end, w_start:w_end, :] += \
                    grad[:, i:i+1, j:j+1, :] * self.mask[:, h_start:h_end, w_start:w_end, :]
                    
        return grad_input

    def compute_output_shape(self):
        """출력 shape 계산"""
        if not hasattr(self, 'input_shape'):
            return None
        batch_size, h, w, channels = self.input_shape
        h_out = h // self.pool_size
        w_out = w // self.pool_size
        return (batch_size, h_out, w_out, channels)

    def count_params(self):
        """파라미터 수 계산"""
        return 0  # MaxPool2D 레이어는 학습 파라미터가 없음