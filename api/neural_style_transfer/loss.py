import torch
import torch.nn as nn

# Content loss
class ContentLoss(nn.Module):
    def __init__(self, weight, normalize=True):
        super(ContentLoss, self).__init__()
        
        self.weight = weight
        self.normalize = normalize
        
        self.mode = 'None'
        self.criterion = nn.MSELoss()
        self.target = torch.Tensor()
        self.loss = 0
        
    def forward(self, input):
        # calculate the loss while passing through this layer
        if self.mode == 'loss':
            loss = self.criterion(input, self.target)
            if self.normalize:
                loss = ScaleGradients.apply(loss, self.weight)
            self.loss = self.weight * loss
        elif self.mode == 'capture':
            self.target = input.detach()
        
        return input


class StyleLoss(nn.Module):
    def __init__(self, weight, normalize=True):
        super(StyleLoss, self).__init__()
        
        self.weight = weight
        self.normalize = normalize
        
        self.mode = 'None'
        self.criterion = nn.MSELoss()
        self.target = torch.Tensor()
        self.loss = 0
    
    def cal_gram_matrix(self, input):
        _, C, H, W = input.size()
        x_flat = input.view(C, H * W)
        return torch.mm(x_flat, x_flat.t())
    
    def forward(self, input):
        # calculate Grad Matrix
        self.G = self.cal_gram_matrix(input)
        self.G = self.G.div(input.nelement())
        
        if self.mode == 'loss':
            loss = self.criterion(self.G, self.target)
            if self.normalize:
                loss = ScaleGradients.apply(loss, self.weight)
            self.loss = self.weight * loss
        elif self.mode == 'capture':
            self.target = self.G.detach()
        
        return input
    
class TVLoss(nn.Module):
    def __init__(self, weight):
        super(TVLoss, self).__init__()
        self.weight = weight
        
    def forward(self, input):
        x_diff = input[:,:,1:,:] - input[:,:,:-1,:]
        y_diff = input[:,:,:,1:] - input[:,:,:,:-1]
        
        self.loss = self.weight * (torch.sum(torch.abs(x_diff)) + torch.sum(torch.abs(y_diff)))
        return input
    
    
class ScaleGradients(torch.autograd.Function):
    @staticmethod
    def forward(self, input_tensor, weight):
        self.weight = weight
        return input_tensor

    @staticmethod
    def backward(self, grad_output):
        grad_output = grad_output.clone()
        grad_output /= (torch.norm(grad_output, keepdim=True) + 1e-8)
        return self.weight * self.weight * grad_output, None
