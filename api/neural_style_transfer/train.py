import time
import torch

from .utils import postprocess
from .utils import print_log

def train(
    model,
    gen_image,
    params,
):
    steps_per_epoch = params['steps_per_epoch']
    optim_state = {
        "max_iter": steps_per_epoch,
        "tolerance_change": -1,
        "tolerance_grad": -1,
    }
    optimizer = torch.optim.LBFGS([gen_image], **optim_state)
    
    def closure():
        optimizer.zero_grad()
        model(gen_image)
        
        loss = 0
        for loss_layer in params['content_losses']:
            loss += loss_layer.loss.to(params['device'])
        
        for loss_layer in params['style_losses']:
            loss += loss_layer.loss.to(params['device'])
        
        loss.backward()
        return loss
    
    cur_epoch = 0
    start = time.time()
    for epoch in range(int(params['epochs'] / steps_per_epoch)):
        optimizer.step(closure)
        epoch = min((epoch + 1) * steps_per_epoch, params['epochs'])
        
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
    
    return postprocess(gen_image)