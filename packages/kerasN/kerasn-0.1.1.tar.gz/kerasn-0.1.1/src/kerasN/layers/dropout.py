import numpy as np
from .base import Layer

class Dropout(Layer):
    """
    Dropout 레이어
    학습 중에 무작위로 뉴런을 비활성화하여 오버피팅을 방지합니다.
    
    Parameters
    ----------
    rate : float
        드롭아웃 비율 (0~1 사이). 비활성화할 뉴런의 비율을 나타냅니다.
    """
    
    def __init__(self, rate):
        super().__init__()
        self.rate = rate
        self.mask = None
        self.training = True
    
    def forward(self, inputs, training=True):
        """
        순전파
        학습 중에는 무작위로 뉴런을 비활성화하고, 
        테스트 시에는 모든 뉴런을 사용합니다.
        """
        self.inputs = inputs
        self.training = training
        
        if training:
            # 무작위 마스크 생성
            self.mask = (np.random.random(inputs.shape) > self.rate)
            # 스케일 조정을 위해 1/(1-rate)를 곱합니다
            return (inputs * self.mask) / (1 - self.rate)
        else:
            return inputs
    
    def backward(self, grad):
        """
        역전파
        마스크를 사용하여 gradient를 전파합니다.
        """
        return grad * self.mask / (1 - self.rate)
    
    def get_config(self):
        """
        레이어 설정을 반환합니다.
        """
        config = super().get_config()
        config.update({
            'rate': self.rate
        })
        return config 