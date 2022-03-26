from .module import Module, Tensor
from .container import Sequential
from . import ops
from .common import normalize


class Conv2d(Module):
    def __init__(self, in_channels, out_channels, kernel_size, padding, stride):
        super().__init__()
        self.kernel = normalize(kernel_size)
        self.padding = normalize(padding)
        self.stride = normalize(stride)
        self.weight = Tensor(shape=[out_channels, in_channels, *self.kernel], dtype='float32', init_method='rand')

    def forward(self, x):
        return ops.conv2d(x, self.weight, self.padding, self.stride)


class BatchNorm2d(Module):
    def __init__(self, num_features, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.running_mean = Tensor(shape=[num_features], dtype='float32')
        self.running_var = Tensor(shape=[num_features], dtype='float32')

    def forward(self, x: Tensor):
        return ops.batch_norm_infer(x, self.running_mean, self.running_var, self.eps)


class Linear(Module):
    def __init__(self, in_features, out_features, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = Tensor(shape=[in_features, out_features], dtype='float32')
        if bias:
            self.bias = Tensor(shape=[out_features], dtype='float32')
        else:
            self.bias = None

    def forward(self, x: Tensor) -> Tensor:
        return ops.matmul(x, self.weight) + self.bias


class Relu(Module):
    def forward(self, x):
        return ops.relu(x)


class MaxPool2d(Module):
    def __init__(self, kernel_size, stride, padding):
        super().__init__()
        self.kernel = kernel_size
        self.stride = stride
        self.padding = padding

    def forward(self, x):
        return ops.max_pool2d(x, self.kernel, self.stride, self.padding)


class AvgPool2d(Module):
    def __init__(self, kernel_size, stride, padding):
        super().__init__()
        self.kernel = kernel_size
        self.stride = stride
        self.padding = padding

    def forward(self, x):
        return ops.avg_pool2d(x, self.kernel, self.stride, self.padding)


class AdaptiveAvgPool2d(Module):
    def __init__(self, output_size):
        super().__init__()
        self.output_size = normalize(output_size)
        assert tuple(self.output_size) == (1, 1), 'current only support this'

    def forward(self, x: Tensor) -> Tensor:
        n, c, h, w = x.shape
        return ops.avg_pool2d(x, kernel=(h, w), stride=(1, 1), padding=(0, 0))