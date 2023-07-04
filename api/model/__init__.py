import torch
import torch.nn as nn
from torchvision import models

from .utils import transform_image
from .loss import ContentStyleLoss
from .train import train

class VGG(nn.Module):
    def __init__(self, all_conv):
        super(VGG, self).__init__()

        self.req_features = all_conv
        self.model = models.vgg19(pretrained=True).features

    def forward(self, x):
        features = []
        for layer_num, layer in enumerate(self.model):
            x = layer(x)
            if str(layer_num) in self.req_features:
                features.append(x)

        return features


def style_transfer(
    content_image,
    style_image,
    image_size,
    timeout_sec,
):
    # configure the device
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    image_size = (image_size, image_size)
    
    content_image = transform_image(content_image, device, image_size)
    style_image = transform_image(style_image, device, image_size)
    gen_image = content_image.clone().requires_grad_(True)

    epochs = 2000
    lr = 1e-2
    alpha = 1
    beta = 1e3
    content_conv = ['2']
    style_conv = ['0', '5', '10', '21']
    all_conv = ['0', '2', '5', '10', '21']

    model = VGG(all_conv=all_conv).to(device).eval()
    optimizer = torch.optim.Adam([gen_image], lr=lr)
    criterion = ContentStyleLoss(
        alpha=alpha,
        beta=beta,
        all_conv=all_conv,
        content_conv=content_conv,
        style_conv=style_conv
    )

    return train(
        model,
        optimizer,
        criterion,
        content_image,
        style_image,
        gen_image,
        epochs,
        device,
        timeout_sec,
    )