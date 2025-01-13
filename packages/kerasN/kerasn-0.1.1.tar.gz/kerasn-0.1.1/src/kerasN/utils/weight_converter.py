import numpy as np
import tensorflow as tf
import json

def convert_tf_to_npy(model_path, save_path, quantized=False):
    """TensorFlow 모델을 npy 형식으로 변환
    
    Parameters:
    -----------
    model_path : str
        TensorFlow 모델 경로
    save_path : str
        저장할 npy 파일 경로
    quantized : bool
        양자화된 모델 여부
    """
    # TensorFlow 모델 로드
    if quantized:
        converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]
        tflite_model = converter.convert()
        interpreter = tf.lite.Interpreter(model_content=tflite_model)
    else:
        model = tf.keras.models.load_model(model_path)
    
    weights = {}
    if quantized:
        interpreter.allocate_tensors()
        details = interpreter.get_tensor_details()
        
        for detail in details:
            name = detail['name']
            tensor = interpreter.get_tensor(detail['index'])
            # 양자화된 값을 원래 값으로 변환
            if detail['dtype'] in [np.uint8, np.int8]:
                scale = detail['quantization'][0]
                zero_point = detail['quantization'][1]
                tensor = (tensor.astype(np.float32) - zero_point) * scale
            weights[name] = tensor
    else:
        for layer in model.layers:
            weights[layer.name] = [w.numpy() for w in layer.weights]
    
    # npy 형식으로 저장
    np.save(save_path, weights)

def download_and_convert_mobilenet(quantized=False):
    """MobileNet 모델 다운로드 및 변환"""
    # TensorFlow Hub에서 모델 다운로드
    if quantized:
        model_url = "https://tfhub.dev/tensorflow/lite-model/mobilenet_v2_1.0_224_quantized/1/default/1"
    else:
        model_url = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/classification/5"
    
    model_path = tf.keras.utils.get_file(
        f"mobilenet_v2_{'quantized_' if quantized else ''}weights",
        model_url,
        untar=True
    )
    
    # 가중치 변환 및 저장
    save_path = f"weights/mobilenet_v2_{'quantized_' if quantized else ''}weights.npy"
    convert_tf_to_npy(model_path, save_path, quantized)
    
    return save_path 