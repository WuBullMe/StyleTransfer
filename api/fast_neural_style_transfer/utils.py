import torch
from PIL import Image
from torchvision import transforms

from .model import Network
from . import check_param

# Preprocess the image before giving it to the model
# Read image, resize, rescale to [0, 1] then to [0, 255]
# and normalize
def preprocess(image, params):
    if params['from_path']:
        # try to open the given file by path
        image = Image.open(image).convert('RGB')
    
    
    loader = transforms.Compose([transforms.Resize(params['image_size']), transforms.ToTensor()])
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


def adjust_learning_rate(optimizer, lr, lr_decay, iteration_count):
    lr /= (1 + lr_decay * iteration_count)
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
        

def build_model(params):
    network = Network().to(params['device'])

    state = network.state_dict()
    
    new_encoder_state_values = iter(torch.load('fast_neural_style_transfer/models/vgg_normalised.pth').values())
    new_decoder_state_values = iter(torch.load('fast_neural_style_transfer/models/decoder.pth').values())
    
    for i, key in enumerate(state):
        if key.startswith('encoder'):
            state[key] = next(new_encoder_state_values)
        elif key.startswith('decoder'):
            state[key] = next(new_decoder_state_values)
            
    network.load_state_dict(state)
    return network


def config_params(params):
    params['lr'] = 4e-3
    params['lr_decay'] = 5e-5
    params['alpha'] = 1
    
def eval(
    network,
    content_image,
    style_image,
    params,
):
    content_feats = network.encoder(content_image)
    style_feats = network.encoder(style_image)
    
    network.eval()
    with torch.no_grad():
        stylized_feats = network.adain(content_feats, style_feats)
        stylized_feats = stylized_feats * params['alpha'] + content_feats * (1 - params['alpha'])
        gen_image = network.decoder(stylized_feats)
    
    return postprocess(gen_image)

def setup_style_transfer(kwds):
    params = {}
    
    # add all parameters that kwds have
    params.update(kwds)
    
    # image_size: default 256
    params['image_size'] = check_param.image_size_(kwds.get('image_size', 256))
    
    # timeout_sec: default 5 sec
    params['timeout_sec'] = check_param.timeout_sec_(kwds.get('timeout_sec', 5))
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    params['device'] = check_param.device_(kwds.get('device', device))
    
    # number of epochs: default 500
    params['epochs'] = check_param.epochs_(kwds.get('epochs', 500))
    
    # content_weight: default 5
    params['content_weight'] = check_param.content_weight_(kwds.get('content_weight', 5e0))
    
    # style_weight: default 1e3
    params['style_weight'] = check_param.style_weight_(kwds.get('style_weight', 1e3))
    
    # tv_weight: default 1e-5
    params['tv_weight'] = check_param.tv_weight_(kwds.get('tv_weight', 1e-5))
    
    # content_layers: default 'relu4_2' (same as in article)
    params['content_layers'] = check_param.content_layers_(kwds.get('content_layers', ('relu4_2')))
    
    # style_layers: default ['relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1'] (same as in article)
    params['style_layers'] = check_param.style_layers_(kwds.get('style_layers', ('relu1_1', 'relu2_1', 'relu3_1', 'relu4_1', 'relu5_1')))
    
    # show logs while program is running or not: default False
    params['logs'] = check_param.logs_(kwds.get('logs', False))
    
    params['steps_per_epoch'] = check_param.steps_per_epoch_(kwds.get('steps_per_epoch', 5), params['epochs'])
    
    params['from_path'] = check_param.from_path_(kwds.get('from_path', True))
    
    params['save_network'] = check_param.save_network_(kwds.get('save_network', False))
    
    return params

def print_log(log, params, end="\n", cond=True):
    if cond and params.get("logs", False):
        print(log, end=end)