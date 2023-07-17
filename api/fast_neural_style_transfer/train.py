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
    optimizer = torch.optim.Adam(network.decoder.parameters(), lr=params['lr_decay'])
    cur_epoch = 0
    start = time.time()
    for epoch in range(params['epochs']):
        optimizer.zero_grad()
        adjust_learning_rate(optimizer, params['lr'], params['lr_decay'], iteration_count=epoch)
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
        torch.save(network.state_dict(), 'models/network.pth')
    
    return network
