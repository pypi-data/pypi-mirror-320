import numpy as np
from .base import Callback

class EarlyStopping:
    def __init__(self, monitor='val_loss', min_delta=0.0001, patience=5, verbose=0):
        self.monitor = monitor
        self.min_delta = min_delta
        self.patience = patience
        self.verbose = verbose
        self.best = float('inf') if 'loss' in monitor else float('-inf')
        self.wait = 0
        self.stopped_epoch = 0
        self.best_weights = None
        
    def on_epoch_end(self, epoch, logs=None):
        current = logs.get(self.monitor)
        if current is None:
            return
        
        if 'loss' in self.monitor:
            # loss 지표는 감소하는 것이 좋음
            if current + self.min_delta < self.best:
                self.best = current
                self.wait = 0
            else:
                self.wait += 1
        else:
            # accuracy 지표는 증가하는 것이 좋음
            if current - self.min_delta > self.best:
                self.best = current
                self.wait = 0
            else:
                self.wait += 1
                
        if self.wait >= self.patience:
            self.stopped_epoch = epoch
            if self.verbose > 0:
                print(f'\nEarly stopping triggered at epoch {epoch+1}')
                print(f'Best {self.monitor}: {self.best:.4f}')
            return True
            
        return False 