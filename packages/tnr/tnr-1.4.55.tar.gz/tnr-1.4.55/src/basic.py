import torch
print(torch.cuda.is_available())

x = torch.ones(10,10).cuda()
print(x)
