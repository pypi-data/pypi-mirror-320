import numpy as np
from .base import Layer
from ..activations import get_activation
from ..utils.conv_utils import im2col, col2im

class Conv2D(Layer):
    def __init__(self, filters, kernel_size, activation=None, padding='valid'):
        super().__init__()
        self.filters = filters
        # kernel_size를 튜플로 변환
        self.kernel_size = (kernel_size, kernel_size) if isinstance(kernel_size, int) else kernel_size
        self.activation_name = activation
        self.activation_fn, self.activation_derivative = get_activation(activation)
        self.kernels = None
        self.bias = None
        self.padding = padding
        # padding='same'인 경우 입력 크기를 유지하도록 패딩
        self.pad = self.kernel_size[0] // 2 if padding == 'same' else 0
        
    def build(self, input_shape):
        """레이어 초기화"""
        if len(input_shape) != 4:
            raise ValueError(f"Conv2D 레이어는 4D 입력이 필요합니다. 입력 shape: {input_shape}")
        
        self.input_shape = input_shape
        channels = input_shape[-1]
        
        # 커널 영역 계산
        kernel_area = self.kernel_size[0] * self.kernel_size[1]
        
        # Xavier/Glorot 초기화
        limit = np.sqrt(6 / (channels * kernel_area + self.filters))
        
        # 가중치 초기화
        self.kernels = np.random.uniform(-limit, limit, 
                                     (self.kernel_size[0], self.kernel_size[1], channels, self.filters))
        self.bias = np.zeros((self.filters,))
        
        # 출력 shape 계산
        h_out = input_shape[1] - self.kernel_size[0] + 1 + 2 * self.pad
        w_out = input_shape[2] - self.kernel_size[1] + 1 + 2 * self.pad
        self.output_shape = (input_shape[0], h_out, w_out, self.filters)
        
    def forward(self, input):
        self.input = input
        batch_size = len(input)
        
        # 패딩 추가
        self.padded_input = np.pad(input, 
                                 ((0,0), (self.pad,self.pad), 
                                  (self.pad,self.pad), (0,0)), 
                                 'constant')
        
        h_out = self.output_shape[1]
        w_out = self.output_shape[2]
        
        # im2col 변환
        self.cols = im2col(self.padded_input, 
                          self.kernel_size[0], 
                          self.kernel_size[1],
                          stride=1, 
                          pad=0)
        
        # 컨볼루션 연산
        kernels_reshaped = self.kernels.reshape(-1, self.filters)
        self.linear_output = np.dot(self.cols.reshape(batch_size * h_out * w_out, -1), 
                                  kernels_reshaped)
        self.linear_output = self.linear_output.reshape(batch_size, h_out, w_out, self.filters)
        self.linear_output += self.bias
        
        # 활성화 함수
        self.output = self.activation_fn(self.linear_output)
        return self.output
        
    def backward(self, grad, learning_rate):
        batch_size = len(grad)
        
        if self.activation_name != 'softmax':
            grad = grad * self.activation_derivative(self.linear_output)
        
        # 그래디언트 클리핑 추가
        grad = np.clip(grad, -1.0, 1.0)
        
        # 그래디언트 reshape
        grad_reshaped = grad.reshape(batch_size * self.output_shape[1] * self.output_shape[2], -1)
        
        # 커널 그래디언트
        cols_reshaped = self.cols.reshape(batch_size * self.output_shape[1] * self.output_shape[2], -1)
        kernels_grad = np.dot(cols_reshaped.T, grad_reshaped)
        kernels_grad = kernels_grad.reshape(self.kernels.shape)
        
        # 그래디언트 클리핑
        kernels_grad = np.clip(kernels_grad, -1.0, 1.0)
        
        # 편향 그래디언트
        bias_grad = np.sum(grad, axis=(0, 1, 2))
        bias_grad = np.clip(bias_grad, -1.0, 1.0)
        
        # 입력 그래디언트
        kernels_reshaped = self.kernels.reshape(-1, self.filters)
        grad_cols = np.dot(grad_reshaped, kernels_reshaped.T)
        grad_cols = grad_cols.reshape(self.cols.shape)
        
        # col2im 변환으로 입력 그래디언트 계산
        grad_input = col2im(grad_cols, 
                           self.input.shape,
                           self.kernel_size[0],
                           self.kernel_size[1],
                           stride=1,
                           pad=self.pad)
        
        # 파라미터 업데이트
        self.kernels -= learning_rate * kernels_grad
        self.bias -= learning_rate * bias_grad
        
        return grad_input

    def compute_output_shape(self):
        """출력 shape 계산"""
        if not hasattr(self, 'input_shape'):
            return None
        
        batch_size, h, w, channels = self.input_shape
        h_out = h - self.kernel_size[0] + 1 + 2 * self.pad
        w_out = w - self.kernel_size[1] + 1 + 2 * self.pad
        return (batch_size, h_out, w_out, self.filters)

    def count_params(self):
        """파라미터 수 계산"""
        if not hasattr(self, 'input_shape'):
            return 0
        
        _, _, _, channels = self.input_shape
        kernel_params = self.kernel_size[0] * self.kernel_size[1] * channels * self.filters
        bias_params = self.filters
        return kernel_params + bias_params