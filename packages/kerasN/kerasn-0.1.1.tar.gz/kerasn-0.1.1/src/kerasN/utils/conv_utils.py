import numpy as np

def im2col(input_data, kernel_height, kernel_width, stride=1, pad=0):
    N, H, W, C = input_data.shape
    out_h = (H + 2*pad - kernel_height)//stride + 1
    out_w = (W + 2*pad - kernel_width)//stride + 1

    img = np.pad(input_data,
                 [(0,0), (pad,pad), (pad,pad), (0,0)],
                 'constant')
    col = np.zeros((N, out_h, out_w, kernel_height*kernel_width*C))

    for y in range(out_h):
        y_start = y * stride
        for x in range(out_w):
            x_start = x * stride
            col[:, y, x, :] = img[:, y_start:y_start+kernel_height,
                                 x_start:x_start+kernel_width, :].reshape(N, -1)

    return col

def col2im(col, input_shape, kernel_height, kernel_width, stride=1, pad=0):
    N, H, W, C = input_shape
    out_h = (H + 2*pad - kernel_height)//stride + 1
    out_w = (W + 2*pad - kernel_width)//stride + 1
    
    img = np.zeros((N, H + 2*pad, W + 2*pad, C))
    
    for y in range(out_h):
        y_start = y * stride
        for x in range(out_w):
            x_start = x * stride
            img[:, y_start:y_start+kernel_height,
                x_start:x_start+kernel_width, :] += col[:, y, x, :].reshape(
                    N, kernel_height, kernel_width, C)
    
    return img[:, pad:H + pad, pad:W + pad, :]