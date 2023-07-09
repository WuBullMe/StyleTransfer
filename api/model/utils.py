import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms
from PIL import Image

# import loss functions
from .loss import ContentLoss, StyleLoss, TVLoss

# Preprocess the image giving it to the model
# Read image, resize, rescale to [0, 1] then to [0, 255]
# and normalize
def preprocess(image_name, image_size):
    try:
        image = Image.open(image_name).convert('RGB')
    except:
        raise IOError(f"Can't open {image_name} file")
    
    loader = transforms.Compose([transforms.Resize(image_size), transforms.ToTensor()])
    normalize = transforms.Compose([
        transforms.Normalize(
            mean=[123.68, 116.779, 103.939],
            std=[1, 1, 1]
        )
    ])
    tensor = normalize(loader(image) * 255).unsqueeze(0)
    return tensor


# Postprocess the output_tensor to normal image to display it
def postprocess(output_tensor):
    normalize = transforms.Compose([
        transforms.Normalize(
            mean=[-123.68, -116.779, -103.939],
            std=[1, 1, 1]
        )
    ])
    output_tensor = normalize(output_tensor.detach().squeeze(0).cpu()) / 255
    output_tensor.clamp_(0, 1)
    image2pil = transforms.ToPILImage()
    image = image2pil(output_tensor.cpu())
    return image


def build_model(params):
    # Fetch the VGG19 to extract image features
    cnn = models.vgg19(weights='DEFAULT', progress=False).features

    content_losses, style_losses, tv_losses = [], [], []
    model = nn.Sequential()
    # add tv_weight as first layer [if we assigned tv_weight]
    if params['tv_weight'] > 0:
        tv_mod = TVLoss(params['tv_weight'])
        model.add_module('tv_loss', tv_mod)
        tv_losses.append(tv_mod)

    # layer, conv, relu, content_loss, style_loss
    cnt = {
        'layer': 1,
        'conv': 0,
        'relu': 0,
        'content_loss': 0,
        'style_loss': 0,
    }

    # build the model, and add loss layer to indicated places
    for layer in list(cnn):
        cur_layer_name = str(len(model))
        if isinstance(layer, nn.MaxPool2d):
            cur_layer_name = f"max_pool{cnt['layer']}"
            cnt['layer'] += 1
            cnt['conv'] = 0
            cnt['relu'] = 0
        if isinstance(layer, nn.Conv2d):
            cnt['conv'] += 1
            cur_layer_name = f"conv{cnt['layer']}_{cnt['conv']}"
        if isinstance(layer, nn.ReLU):
            cnt['relu'] += 1
            cur_layer_name = f"relu{cnt['layer']}_{cnt['relu']}"

        model.add_module(cur_layer_name, layer)
        if cur_layer_name in params['content_layers']:
            cnt['content_loss'] += 1
            loss_module = ContentLoss(params['content_weight'], True)
            model.add_module(f"content_loss_{cnt['content_loss']}", loss_module)
            content_losses.append(loss_module)
        
        if cur_layer_name in params['style_layers']:
            cnt['style_loss'] += 1
            loss_module = StyleLoss(params['style_weight'], True)
            model.add_module(f"style_loss_{cnt['style_loss']}", loss_module)
            style_losses.append(loss_module)

    # add content_losses, style_losses, tv_losses to params
    params['content_losses'] = content_losses
    params['style_losses'] = style_losses
    params['tv_losses'] = tv_losses
    
    return model.to(params["device"])


def config_loss_layers(model, content_image, style_image, params):
    # configure the loss layers
    # Capture content targets
    for i in params['content_losses']:
        i.mode = 'capture'
    model(content_image)
    for i in params['content_losses']:
        i.mode = 'None'
    
    # Capture style targets
    for i in params['style_losses']:
        i.mode = 'capture'
    model(style_image)
    
    # Set all loss modules to loss mode
    for i in params['content_losses']:
        i.mode = 'loss'
    for i in params['style_losses']:
        i.mode = 'loss'
        
    return model


def setup_style_transfer(kwds):
    params = {}
    
    # add all parameters that kwds have
    params.update(kwds)
    
    # image_size: default 256
    params['image_size'] = kwds.get('image_size', 256)
    params['image_size'] = (params['image_size'], params['image_size'])
    
    # timeout_sec: default 5 sec
    params['timeout_sec'] = kwds.get('timeout_sec', 5)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    params['device'] = kwds.get('device', device)
    
    # number of epochs: default 500
    params['epochs'] = kwds.get('epochs', 500)
    
    # content_weight: default 5
    params['content_weight'] = kwds.get('content_weight', 5e0)
    
    # style_weight: default 1e3
    params['style_weight'] = kwds.get('style_weight', 1e3)
    
    # tv_weight: default 1e-5
    params['tv_weight'] = kwds.get('tv_weight', 1e-5)
    
    # content_layers: default 'relu4_2' (same as in article)
    params['content_layers'] = kwds.get('content_layers', ['relu4_2'])
    
    # style_layers: default ['relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1'] (same as in article)
    params['style_layers'] = kwds.get('style_layers', ['relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1'])
    
    params['logs'] = kwds.get('logs', False)
    
    return params

def print_log(log, params, end="\n", cond=True):
    if cond and params.get("logs", False):
        print(log, end=end)