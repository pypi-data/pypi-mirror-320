from statictorch import *
import typing
from torch import Tensor

def work_on(tensors: list[Tensor]):
    ...


my_tensors: list[Tensor0d] = []
work_on(my_tensors)  # Pylance: Argument of type "list[Tensor0d]" cannot be assigned to parameter "tensors" of type "list[Tensor]" in function "work_on"

# To solve the problem:
work_on(typing.cast(list[Tensor], my_tensors))