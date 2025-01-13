import numpy as np
from .base import Layer

class BatchNormalization(Layer):
    """
    배치 정규화 레이어
    
    Parameters
    ----------
    epsilon : float
        수치 안정성을 위한 작은 상수 (기본값: 1e-7)
    momentum : float
        이동 평균을 위한 모멘텀 (기본값: 0.9)
    """
    
    def __init__(self, epsilon=1e-7, momentum=0.9):
        super().__init__()
        self.epsilon = epsilon
        self.momentum = momentum
        self.gamma = None
        self.beta = None
        self.moving_mean = None
        self.moving_var = None
        self.is_training = True
        
        # 역전파에 필요한 캐시
        self.cache = {}
        
    def build(self, input_shape):
        if input_shape is None:
            return
            
        # 입력 shape에 따라 파라미터 초기화
        if len(input_shape) == 4:  # Conv 레이어
            channels = input_shape[-1]
        elif len(input_shape) == 2:  # Dense 레이어
            channels = input_shape[-1]
        else:
            raise ValueError(f"Unexpected input shape: {input_shape}")
            
        # 학습 가능한 파라미터
        self.gamma = np.ones(channels)
        self.beta = np.zeros(channels)
        
        # 이동 평균과 분산
        self.moving_mean = np.zeros(channels)
        self.moving_var = np.ones(channels)
        
    def forward(self, inputs, training=True):
        """
        순전파
        
        Parameters
        ----------
        inputs : numpy.ndarray
            입력 데이터
        training : bool
            학습 모드 여부
            
        Returns
        -------
        numpy.ndarray
            정규화된 출력
        """
        self.is_training = training
        self.input_shape = inputs.shape
        
        # 입력을 2D로 변환
        if len(self.input_shape) == 4:
            N, H, W, C = self.input_shape
            inputs_reshaped = inputs.reshape(-1, C)
        else:
            inputs_reshaped = inputs
            
        if self.is_training:
            # 미니배치의 평균과 분산 계산
            mean = np.mean(inputs_reshaped, axis=0)
            var = np.var(inputs_reshaped, axis=0) + self.epsilon
            
            # 정규화
            x_norm = (inputs_reshaped - mean) / np.sqrt(var)
            
            # 이동 평균 업데이트
            self.moving_mean = self.momentum * self.moving_mean + (1 - self.momentum) * mean
            self.moving_var = self.momentum * self.moving_var + (1 - self.momentum) * var
            
            # 캐시 저장
            self.cache = {
                'x_norm': x_norm,
                'mean': mean,
                'var': var,
                'inputs_reshaped': inputs_reshaped
            }
        else:
            # 테스트 시에는 이동 평균 사용
            x_norm = ((inputs_reshaped - self.moving_mean) / 
                     np.sqrt(self.moving_var + self.epsilon))
        
        # 스케일과 이동
        out = self.gamma * x_norm + self.beta
        
        # 원래 shape으로 복원
        if len(self.input_shape) == 4:
            out = out.reshape(self.input_shape)
            
        return out
        
    def backward(self, grad, learning_rate=None):
        """
        역전파
        
        Parameters
        ----------
        grad : numpy.ndarray
            상위 레이어로부터의 그래디언트
        learning_rate : float
            학습률 (옵션)
            
        Returns
        -------
        numpy.ndarray
            하위 레이어로의 그래디언트
        """
        if learning_rate is not None:
            self.learning_rate = learning_rate
        
        if len(self.input_shape) == 4:
            N, H, W, C = self.input_shape
            grad = grad.reshape(-1, C)
            
        x_norm = self.cache['x_norm']
        mean = self.cache['mean']
        var = self.cache['var']
        inputs_reshaped = self.cache['inputs_reshaped']
        
        N = grad.shape[0]
        
        # 스케일과 이동에 대한 그래디언트
        dgamma = np.sum(grad * x_norm, axis=0)
        dbeta = np.sum(grad, axis=0)
        
        # 정규화된 입력에 대한 그래디언트
        dx_norm = grad * self.gamma
        
        # 분산에 대한 그래디언트
        dvar = np.sum(dx_norm * (inputs_reshaped - mean) * -0.5 * 
                     np.power(var, -1.5), axis=0)
        
        # 평균에 대한 그래디언트
        dmean = np.sum(dx_norm * -1/np.sqrt(var), axis=0) + \
                dvar * np.mean(-2 * (inputs_reshaped - mean), axis=0)
        
        # 입력에 대한 그래디언트
        dx = (dx_norm / np.sqrt(var) + 
              dvar * 2 * (inputs_reshaped - mean) / N + 
              dmean / N)
        
        # 파라미터 업데이트
        if hasattr(self, 'learning_rate') and self.learning_rate is not None:
            self.gamma -= self.learning_rate * dgamma
            self.beta -= self.learning_rate * dbeta
        
        # 원래 shape으로 복원
        if len(self.input_shape) == 4:
            dx = dx.reshape(self.input_shape)
            
        return dx
    
    def train(self):
        """학습 모드로 설정"""
        self.is_training = True
        
    def eval(self):
        """평가 모드로 설정"""
        self.is_training = False
        
    def get_config(self):
        """설정 반환"""
        config = super().get_config()
        config.update({
            'epsilon': self.epsilon,
            'momentum': self.momentum
        })
        return config

    def compute_output_shape(self):
        """출력 shape 계산"""
        if not hasattr(self, 'input_shape'):
            return None
        return self.input_shape

    def count_params(self):
        """파라미터 수 계산"""
        if not hasattr(self, 'input_shape'):
            return 0
        channels = self.input_shape[-1]
        return 2 * channels  # gamma + beta 