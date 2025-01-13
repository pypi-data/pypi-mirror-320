from .base import QuantizedModel
import numpy as np

class MobileNetV3(QuantizedModel):
    def __init__(self, input_shape=None):
        super().__init__('mobilenet_v3', input_shape)
        
    def extract_features(self, X):
        """특징 추출 (마지막 레이어 이전까지)"""
        X = self.preprocess_input(X)
        
        # 여기서 실제 추론 수행
        # 실제 구현에서는 모든 레이어를 순차적으로 처리
        # 지금은 간단히 마지막 레이어 직전의 특징만 반환
        
        feature_name = list(self.weights.keys())[-2]  # 마지막 레이어 이전
        features = self.weights[feature_name]
        
        # 양자화 해제
        quant = self.quantization[feature_name]
        features = (np.array(features).astype(np.float32) - 
                   quant['zero_point']) * quant['scale']
        
        return features 