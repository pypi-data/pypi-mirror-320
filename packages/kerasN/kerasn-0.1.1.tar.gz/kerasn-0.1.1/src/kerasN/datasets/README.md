# KerasN Datasets

KerasN은 다양한 데이터셋을 제공하며, 일반 Python 환경과 Pyodide(웹브라우저) 환경 모두에서 사용할 수 있습니다.

## 지원하는 데이터셋

### 기본 데이터셋 (sklearn)
- `digits`: 0-9 손글씨 숫자 (8x8 이미지)
- `iris`: 붓꽃 분류 데이터
- `breast_cancer`: 유방암 진단 데이터
- `wine`: 와인 분류 데이터

### 이미지 데이터셋
- `mnist`: MNIST 손글씨 숫자 (28x28 흑백)
- `fashion_mnist`: Fashion-MNIST 의류 이미지 (28x28 흑백)
- `cifar10`: CIFAR-10 컬러 이미지 (32x32 컬러)

## 사용 방법

```python
from kerasN.datasets import load_data

# 기본 데이터셋 로드
X, y = load_data('iris', normalize=True)
X, y = load_data('digits', normalize=True, reshape_to_image=True)  # 8x8x1 이미지로 변환

# 이미지 데이터셋 로드
X, y = load_data('mnist', normalize=True, reshape_to_image=True)  # 28x28x1 이미지로 변환
X, y = load_data('fashion_mnist', normalize=True, reshape_to_image=True)
```

## 데이터 저장 위치
- 일반 Python 환경: `kerasN/datasets/data` 디렉토리에 `.npy` 형식으로 저장
- Pyodide 환경: 가상 파일시스템에 임시 저장

## 데이터 전처리 옵션
- `normalize`: 데이터를 0-1 범위로 정규화 (기본값: True)
- `reshape_to_image`: 이미지 형태로 reshape (기본값: False)
  - MNIST, Fashion-MNIST: (N, 28, 28, 1)
  - CIFAR-10: (N, 32, 32, 3)
  - Digits: (N, 8, 8, 1)
```
