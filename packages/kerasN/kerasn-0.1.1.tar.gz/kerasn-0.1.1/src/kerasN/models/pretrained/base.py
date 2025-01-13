import numpy as np
import json
import os

class QuantizedModel:
    def __init__(self, model_name, input_shape=None):
        self.model_name = model_name
        self.weights = None
        self.config = None
        self.quantization = None
        self.load_model()
        
        if input_shape:
            self.config['input_shape'] = input_shape
    
    def load_model(self):
        """모델 가중치와 설정 로드"""
        base_path = os.path.join(os.path.dirname(__file__), 'weights')
        weights_path = os.path.join(base_path, f'{self.model_name}_weights.npy')
        config_path = os.path.join(base_path, f'{self.model_name}_config.json')
        
        self.weights = np.load(weights_path, allow_pickle=True).item()
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.quantization = self.config['quantization']
    
    def preprocess_input(self, X):
        """입력 데이터 전처리"""
        input_name = list(self.weights.keys())[0]
        input_quant = self.quantization[input_name]
        X_quantized = X / input_quant['scale'] + input_quant['zero_point']
        return X_quantized.astype(np.uint8)
    
    def extract_features(self, X):
        """특징 추출 (하위 클래스에서 구현)"""
        raise NotImplementedError 