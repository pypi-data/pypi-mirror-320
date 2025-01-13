def transfer_learning(base_model, num_classes, freeze_layers=None):
    """Transfer Learning을 위한 모델 설정
    
    Parameters:
    -----------
    base_model : Sequential
        기본 모델 (예: VGG16, ResNet50 등)
    num_classes : int
        타겟 클래스 수
    freeze_layers : int or None
        고정할 레이어 수 (None이면 자동 설정)
    
    Returns:
    --------
    model : Sequential
        Transfer Learning을 위한 모델
    """
    # 기존 분류층 제거
    if hasattr(base_model.layers[-1], 'units'):
        base_model.layers.pop()  # 마지막 Dense 레이어 제거
    
    # 레이어 고정
    if freeze_layers is not None:
        for layer in base_model.layers[:freeze_layers]:
            layer.trainable = False
    
    # 새로운 분류층 추가
    base_model.add(Dense(num_classes, activation='softmax'))
    
    return base_model 