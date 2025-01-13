import torch
from statictorch import *

def f_2d(x: Tensor2d):
    print(x)

tensor1 = torch.zeros([2, 3])
f_2d(tensor1)

tensor2 = Tensor2d(torch.zeros([2, 3]))
f_2d(tensor2)

class Batch(TensorDimensionDescriptor):
    pass

tensor3: Tensor2d[Batch, Batch] = Tensor2d(torch.zeros([2, 3]))
f_2d(tensor3)
