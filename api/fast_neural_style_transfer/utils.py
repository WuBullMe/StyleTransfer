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


def adjust_learning_rate(optimizer, cur_epochs, params):
    lr = params['lr']
    lr_decay = params['lr_decay']
    lr /= (1 + lr_decay * cur_epochs)
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
    
def setup_style_transfer(kwds):
    params = {}
    
    # add all parameters that kwds have
    params.update(kwds)
    
    # image_size: default 512
    params['image_size'] = check_param.image_size_(kwds.get('image_size', 512))
    
    # timeout_sec: default 5 sec
    params['timeout_sec'] = check_param.timeout_sec_(kwds.get('timeout_sec', 5))
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    params['device'] = check_param.device_(kwds.get('device', device))
    
    # number of epochs: default 30
    params['epochs'] = check_param.epochs_(kwds.get('epochs', 30))
    
    # content_weight: default 5
    params['content_weight'] = check_param.content_weight_(kwds.get('content_weight', 5e0))
    
    # style_weight: default 2e2
    params['style_weight'] = check_param.style_weight_(kwds.get('style_weight', 2e2))
    
    # alpha: default 1
    params['alpha'] = check_param.alpha_(kwds.get('alpha', 1))
    
    # show logs while program is running or not: default False
    params['logs'] = check_param.logs_(kwds.get('logs', False))
    
    params['from_path'] = check_param.from_path_(kwds.get('from_path', True))
    
    params['save_network'] = check_param.save_network_(kwds.get('save_network', False))
    
    params['train'] = check_param.train_(kwds.get('train', True))
    
    return params

def print_log(log, params, end="\n", cond=True):
    if cond and params.get("logs", False):
        print(log, end=end)