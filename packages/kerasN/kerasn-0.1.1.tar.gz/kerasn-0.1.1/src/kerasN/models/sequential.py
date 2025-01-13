import numpy as np
from ..layers import Layer, Input, Conv2D, Dense, BatchNormalization
from ..utils.progress_bar import ProgressBar
import json
from ..utils.visualization import TrainingVisualizer

class Sequential:
    def __init__(self, layers=None):
        self.layers = []
        self.built = False
        self.compiled = False
        self.verbose = True
        
        # 리스트로 레이어 초기화 지원
        if layers is not None:
            if not isinstance(layers, list):
                layers = [layers]
            for layer in layers:
                self.add(layer)
    
    def add(self, layer):
        """레이어 추가"""
        if not isinstance(layer, Layer):
            raise TypeError("레이어는 Layer 클래스의 인스턴스여야 합니다.")
        
        # Input 레이어인 경우 input_shape 설정
        if isinstance(layer, Input):
            layer.input_shape = (None,) + layer.shape
            self.built = True
        # 이전 레이어가 있는 경우 현재 레이어의 input_shape 설정
        elif self.layers:
            prev_layer = self.layers[-1]
            if hasattr(prev_layer, 'compute_output_shape'):
                input_shape = prev_layer.compute_output_shape()
                layer.input_shape = input_shape
                if hasattr(layer, 'build'):
                    layer.build(input_shape)
        
        self.layers.append(layer)
    
    def compile(self, loss='categorical_crossentropy', learning_rate=0.01):
        """모델 컴파일"""
        self.loss = loss
        self.learning_rate = learning_rate
        self.compiled = True
        
        # 모든 레이어의 build 상태 확인 및 초기화
        if not self.built:
            raise RuntimeError("첫 번째 레이어로 Input 레이어가 필요합니다.")
        
        # 각 레이어의 input_shape와 build 확인
        for i, layer in enumerate(self.layers[1:], 1):  # Input 레이어 제외
            prev_layer = self.layers[i-1]
            input_shape = prev_layer.compute_output_shape()
            
            if not hasattr(layer, 'input_shape'):
                layer.input_shape = input_shape
            if hasattr(layer, 'build'):
                layer.build(input_shape)
    
    def fit(self, X, y, epochs=10, batch_size=32, validation_split=0.0, callbacks=None, verbose=True):
        """모델 학습"""
        if not self.compiled:
            raise RuntimeError("모델을 먼저 컴파일해야 합니다.")
            
        self.verbose = verbose
        
        # 검증 데이터 분할
        n_samples = len(X)
        n_val = int(n_samples * validation_split)
        train_idx = np.random.permutation(n_samples)
        
        X_train = X[train_idx[n_val:]]
        y_train = y[train_idx[n_val:]]
        X_val = X[train_idx[:n_val]]
        y_val = y[train_idx[:n_val]]
        
        callbacks = callbacks or []
        visualizer = TrainingVisualizer()
        
        # 콜백에 모델 연결
        for callback in callbacks:
            callback.model = self
        
        n_samples = len(X_train)
        n_batches = (n_samples + batch_size - 1) // batch_size
        
        for epoch in range(epochs):
            if self.verbose:
                print(f'\nEpoch {epoch + 1}/{epochs}')
                progress_bar = ProgressBar(n_batches)
            
            # 데이터 셔플
            idx = np.random.permutation(n_samples)
            X_train = X_train[idx]
            y_train = y_train[idx]
            
            train_loss = 0
            train_acc = 0
            
            # 학습
            for b in range(n_batches):
                start_idx = b * batch_size
                end_idx = min((b + 1) * batch_size, n_samples)
                batch_X = X_train[start_idx:end_idx]
                batch_y = y_train[start_idx:end_idx]
                
                # 순전파
                output = batch_X
                for layer in self.layers:
                    output = layer.forward(output)
                
                # 손실 계산
                if self.loss == 'categorical_crossentropy':
                    batch_loss = -np.sum(batch_y * np.log(np.clip(output, 1e-10, 1.0)))
                    train_loss += batch_loss
                    batch_acc = np.sum(np.argmax(output, axis=1) == np.argmax(batch_y, axis=1))
                    train_acc += batch_acc
                    grad = output - batch_y
                
                # 역전파
                for layer in reversed(self.layers):
                    grad = layer.backward(grad, self.learning_rate)
                
                if self.verbose:
                    current_loss = train_loss / (end_idx)
                    current_acc = train_acc / (end_idx)
                    metrics = {
                        'loss': current_loss,
                        'accuracy': current_acc
                    }
                    progress_bar.update(b + 1, metrics)
            
            # 검증
            val_output = self.predict(X_val)
            val_loss = -np.mean(y_val * np.log(np.clip(val_output, 1e-10, 1.0)))
            val_acc = np.mean(np.argmax(val_output, axis=1) == np.argmax(y_val, axis=1))
            
            # 에폭 종료 후 로그 생성
            logs = {
                'loss': train_loss / n_samples,
                'accuracy': train_acc / n_samples,
                'val_loss': val_loss,
                'val_accuracy': val_acc
            }
            
            if self.verbose:
                print(f" - val_loss: {val_loss:.4f} - val_accuracy: {val_acc:.4f}")
            
            # 시각화 데이터 업데이트
            visualizer.update(logs)
            
            # 콜백 처리
            if callbacks:
                for callback in callbacks:
                    if hasattr(callback, 'on_epoch_end'):
                        stop_training = callback.on_epoch_end(epoch, logs)
                        if stop_training:
                            if self.verbose:
                                print("\nTraining stopped early")
                            return visualizer
        
        # 학습 완료 후 그래프 저장
        visualizer.save('training_history.png')
        return visualizer
    
    def predict(self, X):
        """예측 수행"""
        output = X
        for layer in self.layers:
            output = layer.forward(output)
        return output
    
    def evaluate(self, X, y):
        """모델 평가"""
        output = self.predict(X)
        if self.loss == 'categorical_crossentropy':
            loss = -np.mean(y * np.log(np.clip(output, 1e-10, 1.0)))
            acc = np.mean(np.argmax(output, axis=1) == np.argmax(y, axis=1))
            return loss, acc
        return None
    
    def summary(self):
        """모델 구조 출력"""
        print("\nModel Summary:")
        print("_" * 75)
        print("{:<20} {:<20} {:<20} {:<15}".format(
            "Layer (type)", "Output Shape", "Param #", "Connected to"
        ))
        print("=" * 75)
        
        total_params = 0
        trainable_params = 0
        
        prev_layer_name = "Input"
        for i, layer in enumerate(self.layers):
            # 레이어 이름과 타입
            layer_name = f"{layer.__class__.__name__}_{i}"
            
            # 출력 shape
            if hasattr(layer, 'compute_output_shape'):
                output_shape = str(layer.compute_output_shape()[1:])  # 배치 차원 제외
            else:
                output_shape = "unknown"
            
            # 파라미터 수 계산
            params = layer.count_params() if hasattr(layer, 'count_params') else 0
            total_params += params
            trainable_params += params
            
            # 출력 포맷팅
            print("{:<20} {:<20} {:<20} {:<15}".format(
                layer_name,
                output_shape,
                str(params),
                prev_layer_name
            ))
            
            prev_layer_name = layer_name
        
        print("=" * 75)
        print(f"Total params: {total_params:,}")
        print(f"Trainable params: {trainable_params:,}")
        print(f"Non-trainable params: 0")
        print("_" * 75 + "\n")
    
    def save_weights(self, filepath):
        """모델 가중치 저장"""
        weights = {}
        for i, layer in enumerate(self.layers):
            layer_weights = {}
            if hasattr(layer, 'kernels'):
                layer_weights['kernels'] = layer.kernels.tolist()
            if hasattr(layer, 'bias'):
                layer_weights['bias'] = layer.bias.tolist()
            if hasattr(layer, 'gamma'):
                layer_weights['gamma'] = layer.gamma.tolist()
            if hasattr(layer, 'beta'):
                layer_weights['beta'] = layer.beta.tolist()
            if layer_weights:
                weights[f'layer_{i}'] = layer_weights
        
        with open(filepath, 'w') as f:
            json.dump(weights, f)
    
    def load_weights(self, filepath):
        """모델 가중치 로드"""
        with open(filepath, 'r') as f:
            weights = json.load(f)
        
        for layer_name, layer_weights in weights.items():
            layer_idx = int(layer_name.split('_')[1])
            layer = self.layers[layer_idx]
            
            if 'kernels' in layer_weights:
                layer.kernels = np.array(layer_weights['kernels'])
            if 'bias' in layer_weights:
                layer.bias = np.array(layer_weights['bias'])
            if 'gamma' in layer_weights:
                layer.gamma = np.array(layer_weights['gamma'])
            if 'beta' in layer_weights:
                layer.beta = np.array(layer_weights['beta'])