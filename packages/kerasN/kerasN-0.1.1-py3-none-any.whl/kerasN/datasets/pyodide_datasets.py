import numpy as np
import gzip
import sys
import urllib.request

def is_pyodide():
    return 'pyodide' in sys.modules

if is_pyodide():
    from pyodide.http import open_url
    import pyodide

def download_data(url):
    if is_pyodide():
        return open_url(url).read()
    else:
        return urllib.request.urlopen(url).read()

def save_file(filename, data):
    if is_pyodide():
        pyodide.FS.writeFile(filename, data)
    else:
        with open(filename, 'wb') as f:
            f.write(data)

def load_pyodide_dataset(name, normalize=True, reshape_to_image=False):
    """Pyodide 환경에서 데이터셋을 로드합니다."""
    
    if name == 'fashion_mnist':
        return load_fashion_mnist_pyodide(normalize, reshape_to_image)
    elif name == 'mnist':
        return load_mnist_pyodide(normalize, reshape_to_image)
    elif name == 'cifar10':
        return load_cifar10_pyodide(normalize, reshape_to_image)
    else:
        raise ValueError(f"Dataset {name} not supported in Pyodide environment")

def load_fashion_mnist_pyodide(normalize=True, reshape_to_image=False):
    """Pyodide 환경에서 Fashion-MNIST 데이터를 로드합니다."""
    base_url = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/"
    files = {
        "train_images": "train-images-idx3-ubyte.gz",
        "train_labels": "train-labels-idx1-ubyte.gz",
        "test_images": "t10k-images-idx3-ubyte.gz",
        "test_labels": "t10k-labels-idx1-ubyte.gz",
    }

    def download_to_fs(filename, url):
        if not pyodide.FS.analyzePath(filename)["exists"]:
            print(f"Downloading {filename}...")
            data = open_url(url).read()
            pyodide.FS.writeFile(filename, data)

    def load_from_fs(filename, offset):
        with gzip.open(pyodide.FS.open(filename, "rb"), "rb") as f:
            return np.frombuffer(f.read(), dtype=np.uint8, offset=offset)

    # 파일 다운로드
    for key, filename in files.items():
        download_to_fs(filename, base_url + filename)

    # 데이터 로드
    X = load_from_fs(files["train_images"], 16).reshape(-1, 28, 28)
    y = load_from_fs(files["train_labels"], 8)

    if normalize:
        X = X.astype('float32') / 255.0

    if reshape_to_image:
        X = X.reshape(-1, 28, 28, 1)

    return X, y

def load_mnist_pyodide(normalize=True, reshape_to_image=False):
    """Pyodide 환경에서 MNIST 데이터를 로드합니다."""
    base_url = "http://yann.lecun.com/exdb/mnist/"
    files = {
        "train_images": "train-images-idx3-ubyte.gz",
        "train_labels": "train-labels-idx1-ubyte.gz",
        "test_images": "t10k-images-idx3-ubyte.gz",
        "test_labels": "t10k-labels-idx1-ubyte.gz",
    }

    def download_to_fs(filename, url):
        if not pyodide.FS.analyzePath(filename)["exists"]:
            print(f"Downloading {filename}...")
            data = open_url(url).read()
            pyodide.FS.writeFile(filename, data)

    def load_from_fs(filename, offset):
        with gzip.open(pyodide.FS.open(filename, "rb"), "rb") as f:
            return np.frombuffer(f.read(), dtype=np.uint8, offset=offset)

    # 파일 다운로드 및 데이터 로드
    for key, filename in files.items():
        download_to_fs(filename, base_url + filename)

    X = load_from_fs(files["train_images"], 16).reshape(-1, 28, 28)
    y = load_from_fs(files["train_labels"], 8)

    if normalize:
        X = X.astype('float32') / 255.0
    if reshape_to_image:
        X = X.reshape(-1, 28, 28, 1)
    return X, y

def load_cifar10_pyodide(normalize=True, reshape_to_image=False):
    """Pyodide 환경에서 CIFAR-10 데이터를 로드합니다."""
    url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    # CIFAR-10 구현은 복잡성으로 인해 샘플 데이터만 제공
    raise NotImplementedError("CIFAR-10 is not yet supported in Pyodide environment") 