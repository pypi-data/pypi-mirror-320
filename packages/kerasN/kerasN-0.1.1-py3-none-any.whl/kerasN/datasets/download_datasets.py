import os
import numpy as np
from sklearn.datasets import fetch_openml, load_iris, load_digits, load_breast_cancer, load_wine
import urllib.request
import gzip
import pickle
import tarfile

def ensure_dir(directory):
    """디렉토리가 없으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def download_mnist():
    """MNIST 데이터셋 다운로드"""
    print("Downloading MNIST dataset...")
    mnist = fetch_openml('mnist_784', version=1, as_frame=False)
    X = mnist.data.reshape(-1, 28, 28)
    y = mnist.target.astype(np.int32)
    return X, y

def download_fashion_mnist():
    """Fashion MNIST 데이터셋 다운로드"""
    print("Downloading Fashion-MNIST dataset...")
    base_url = 'http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/'
    files = {
        'train_img': 'train-images-idx3-ubyte.gz',
        'train_lbl': 'train-labels-idx1-ubyte.gz',
        'test_img': 't10k-images-idx3-ubyte.gz',
        'test_lbl': 't10k-labels-idx1-ubyte.gz'
    }
    
    def load_mnist_file(filename, offset):
        with gzip.open(filename, 'rb') as f:
            data = np.frombuffer(f.read(), np.uint8, offset=offset)
        return data
    
    # 데이터 다운로드
    for f in files.values():
        if not os.path.exists(f):
            urllib.request.urlretrieve(base_url + f, f)
    
    # 이미지와 레이블 로드
    X_train = load_mnist_file(files['train_img'], 16).reshape(-1, 28, 28)
    y_train = load_mnist_file(files['train_lbl'], 8)
    X_test = load_mnist_file(files['test_img'], 16).reshape(-1, 28, 28)
    y_test = load_mnist_file(files['test_lbl'], 8)
    
    # 데이터 합치기
    X = np.concatenate([X_train, X_test])
    y = np.concatenate([y_train, y_test])
    
    # 임시 파일 삭제
    for f in files.values():
        if os.path.exists(f):
            os.remove(f)
            
    return X, y

def download_cifar10():
    """CIFAR-10 데이터셋 다운로드"""
    print("Downloading CIFAR-10 dataset...")
    url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    filename = "cifar-10-python.tar.gz"
    
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)
    
    def unpickle(file):
        with open(file, 'rb') as fo:
            dict = pickle.load(fo, encoding='bytes')
        return dict
    
    # 압축 해제 (보안 필터 추가)
    with tarfile.open(filename, 'r:gz') as tar:
        # 안전한 경로인지 확인
        def is_safe_path(path):
            return not path.startswith(('/','..'))
        
        # 모든 멤버의 경로 검사
        members = []
        for member in tar.getmembers():
            if is_safe_path(member.name):
                members.append(member)
            else:
                print(f"Skipping potentially unsafe path: {member.name}")
        
        # 안전한 멤버만 추출
        tar.extractall(members=members)
    
    # 데이터 로드
    data_dir = 'cifar-10-batches-py'
    X = []
    y = []
    
    # 학습 데이터
    for i in range(1, 6):
        batch_file = os.path.join(data_dir, f'data_batch_{i}')
        if os.path.exists(batch_file):  # 파일 존재 확인
            batch_data = unpickle(batch_file)
            X.append(batch_data[b'data'])
            y.extend(batch_data[b'labels'])
    
    # 테스트 데이터
    test_batch = os.path.join(data_dir, 'test_batch')
    if os.path.exists(test_batch):  # 파일 존재 확인
        test_batch = unpickle(test_batch)
        X.append(test_batch[b'data'])
        y.extend(test_batch[b'labels'])
    
    # 데이터 변환
    X = np.concatenate(X).reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    y = np.array(y)
    
    # 임시 파일 정리
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(data_dir):
        import shutil
        shutil.rmtree(data_dir)
    
    return X, y

def download_and_save_dataset(name):
    """데이터셋을 다운로드하고 저장합니다."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    if name == 'mnist':
        X, y = download_mnist()
    elif name == 'fashion_mnist':
        X, y = download_fashion_mnist()
    elif name == 'cifar10':
        X, y = download_cifar10()
    else:
        raise ValueError(f"Unknown dataset: {name}")
        
    np.save(os.path.join(data_dir, f'{name}_data.npy'), X)
    np.save(os.path.join(data_dir, f'{name}_target.npy'), y)
    return X, y

def main():
    """모든 데이터셋 다운로드 및 저장"""
    datasets = ['mnist', 'fashion_mnist', 'cifar10']
    for name in datasets:
        download_and_save_dataset(name)
    print("All datasets have been downloaded and saved successfully!")

if __name__ == '__main__':
    main() 