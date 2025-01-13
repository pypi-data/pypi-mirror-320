import sys
import time

class ProgressBar:
    def __init__(self, total, width=30):
        self.total = total
        self.width = width
        self.start_time = time.time()
        
    def update(self, current, values=None):
        """진행 상태 업데이트"""
        bar_length = int(self.width * current / self.total)
        bar = '=' * bar_length + '-' * (self.width - bar_length)
        
        # 시간 계산
        elapsed_time = time.time() - self.start_time
        steps_per_sec = current / elapsed_time if elapsed_time > 0 else 0
        
        # 진행률 계산
        progress = f"{current}/{self.total}"
        
        # 메트릭 문자열 생성
        metrics_str = ""
        if values:
            metrics_str = " - " + " - ".join(f"{k}: {v:.4f}" for k, v in values.items())
        
        # 진행 바 출력
        sys.stdout.write(
            f"\r{progress} [" + bar + "]" + 
            f" - {steps_per_sec:.1f} steps/s" +
            metrics_str
        )
        sys.stdout.flush()
        
        if current == self.total:
            sys.stdout.write('\n')
