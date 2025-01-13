def progress_bar(current, total, prefix='', suffix='', decimals=1, length=30):
    """진행률 표시"""
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (current / float(total)))
    filled = int(length * current // total)
    bar = '━' * filled + '─' * (length - filled)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='')
    if current == total:
        print()