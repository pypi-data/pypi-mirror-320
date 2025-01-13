import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from kerasN.models import Sequential
from kerasN.layers import Dense, Conv2D, MaxPool2D, Flatten, BatchNormalization, Input
from kerasN.datasets import load_data
from kerasN.utils import to_categorical, train_test_split

class TestKerasN(unittest.TestCase):
    def setUp(self):
        """테스트에 필요한 기본 설정"""
        # 작은 데이터셋으로 테스트
        self.X, self.y = load_data('digits', normalize=True, reshape_to_image=True)
        self.y = to_categorical(self.y)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2
        )

    def test_package_import(self):
        """패키지 임포트 테스트"""
        import kerasN
        self.assertIsNotNone(kerasN.__version__)

    def test_model_creation(self):
        """모델 생성 테스트"""
        model = Sequential([
            Input(shape=(8, 8, 1)),
            Conv2D(16, kernel_size=3, activation='relu', padding='same'),
            BatchNormalization(),
            MaxPool2D(pool_size=2),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(10, activation='softmax')
        ])
        self.assertIsNotNone(model)

    def test_model_compile(self):
        """모델 컴파일 테스트"""
        model = Sequential([
            Input(shape=(8, 8, 1)),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(10, activation='softmax')
        ])
        model.compile(loss='categorical_crossentropy', learning_rate=0.001)
        self.assertTrue(hasattr(model, 'loss'))
        self.assertTrue(hasattr(model, 'learning_rate'))

    def test_model_training(self):
        """모델 학습 테스트"""
        model = Sequential([
            Input(shape=(8, 8, 1)),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(10, activation='softmax')
        ])
        model.compile(loss='categorical_crossentropy', learning_rate=0.001)
        
        # 작은 배치로 1 에폭 학습
        history = model.fit(
            self.X_train[:32], 
            self.y_train[:32],
            epochs=1,
            batch_size=32,
            validation_split=0.2
        )
        
        self.assertIsNotNone(history)
        self.assertTrue(hasattr(history, 'history'))
        self.assertIn('loss', history.history)

    def test_model_prediction(self):
        """모델 예측 테스트"""
        model = Sequential([
            Input(shape=(8, 8, 1)),
            Flatten(),
            Dense(64, activation='relu'),
            Dense(10, activation='softmax')
        ])
        model.compile(loss='categorical_crossentropy', learning_rate=0.001)
        
        predictions = model.predict(self.X_test[:10])
        self.assertEqual(predictions.shape, (10, 10))
        self.assertTrue(np.allclose(np.sum(predictions, axis=1), 1.0))

if __name__ == '__main__':
    unittest.main(verbosity=2) 