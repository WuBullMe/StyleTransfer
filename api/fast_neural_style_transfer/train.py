import time
import torch

from .utils import postprocess
from .utils import print_log
from .utils import adjust_learning_rate

def train(
    network,
    content_image,
    style_image,
    params,
):  
    optimizer = torch.optim.Adam(network.decoder.parameters(), lr=params['lr'])
    cur_epoch = 0
    start = time.time()
    for epoch in range(params['epochs']):
        optimizer.zero_grad()
        adjust_learning_rate(optimizer, epoch, params)
        content_loss, style_loss = network(content_image, style_image)
        total_loss = params['content_weight'] * content_loss + params['style_weight'] * style_loss
        total_loss.backward()
        optimizer.step()
        
        epoch = epoch + 1
        progress = epoch / params['epochs'] * 100
        progress_bar = f"[{'=' * int(progress // 2)}{' ' * (50 - int(progress // 2))}] ({epoch}/{params['epochs']}) {progress:.1f}%"
        print_log(progress_bar, params, end="\r")
        
        cur_epoch = epoch
        elapsed_time = time.time() - start
        if elapsed_time > params['timeout_sec']:
            break
    
    print_log("\nTraining Finished", params)
    
    # add 'completed_epochs': 'cur_epochs/epochs', 'time': end - start
    params['elapsed_time'] = elapsed_time
    params['completed_epochs'] = cur_epoch
    
    if params['save_network']:
        torch.save(network.state_dict(), f"fast_neural_style_transfer/models/network.pth")
    
    return network


def evaluate(
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