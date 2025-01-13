import os
import numpy as np
import json
from .base import Callback

class ModelCheckpoint(Callback):
    def __init__(
        self,
        filepath,
        monitor='val_loss',
        verbose=0,
        save_best_only=True,
        mode='auto'
    ):
        super().__init__()
        self.filepath = filepath
        self.monitor = monitor
        self.verbose = verbose
        self.save_best_only = save_best_only
        
        # 모드 설정
        if mode not in ['auto', 'min', 'max']:
            mode = 'auto'
        if mode == 'min' or (mode == 'auto' and 'loss' in monitor):
            self.monitor_op = np.less
            self.best = np.Inf
        else:
            self.monitor_op = np.greater
            self.best = -np.Inf
            
        # 저장 디렉토리 생성
        dirname = os.path.dirname(filepath)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        current = logs.get(self.monitor)
        
        if current is None:
            return
        
        if self.monitor_op(current, self.best):
            if self.verbose > 0:
                print(f'\nEpoch {epoch + 1}: {self.monitor} improved from {self.best:.4f} to {current:.4f}, saving model')
            self.best = current
            self.model.save_weights(self.filepath)
        elif self.verbose > 0:
            print(f'\nEpoch {epoch + 1}: {self.monitor} did not improve from {self.best:.4f}') 