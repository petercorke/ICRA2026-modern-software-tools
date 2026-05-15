import torch
import torch.nn.functional as F

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("MPS available:", torch.backends.mps.is_available())


y = torch.tensor([1.0])                    # target
x = torch.tensor([1.1])                    # input
w = torch.tensor([2.2], requires_grad=True)
b = torch.tensor([0.0], requires_grad=True)

z = x * w + b
a = torch.sigmoid(z)
loss = F.binary_cross_entropy(a, y)
loss.backward()

print("loss:", loss.item())