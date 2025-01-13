import matplotlib.pyplot as plt

class TrainingVisualizer:
    def __init__(self):
        self.history = {
            'loss': [],
            'accuracy': [],
            'val_loss': [],
            'val_accuracy': []
        }
    
    def update(self, logs):
        """에폭마다 지표 업데이트"""
        for metric in self.history.keys():
            if metric in logs:
                self.history[metric].append(logs[metric])
    
    def plot(self):
        """학습 히스토리 시각화"""
        # seaborn 스타일 제거하고 기본 스타일 사용
        plt.figure(figsize=(12, 4))
        
        # 손실 그래프
        plt.subplot(1, 2, 1)
        plt.plot(self.history['loss'], label='train')
        if 'val_loss' in self.history:
            plt.plot(self.history['val_loss'], label='validation')
        plt.title('Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # 정확도 그래프
        plt.subplot(1, 2, 2)
        plt.plot(self.history['accuracy'], label='train')
        if 'val_accuracy' in self.history:
            plt.plot(self.history['val_accuracy'], label='validation')
        plt.title('Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        return plt.gcf()
    
    def save(self, filepath='training_history.png'):
        """그래프를 이미지로 저장"""
        fig = self.plot()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def get_history_dict(self):
        """학습 히스토리 딕셔너리 반환"""
        return self.history 