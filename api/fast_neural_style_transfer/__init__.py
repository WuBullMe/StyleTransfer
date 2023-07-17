"""Style Transfer Model
    Given two images, transfer style of the second image to the first one.
    It's called Neural Style Tranfer.

    For more information about this algorithm, read this article in which this
    method was provided, i recommend you to read this article,
    Article: https://arxiv.org/pdf/1703.06868.pdf
"""
import torch

from .utils import setup_style_transfer
from .utils import preprocess
from .utils import print_log
from .utils import build_model
from .utils import config_params
from .utils import eval
from .train import train

__version__ = "1.0.0"
__name__ = "fast_neural_style_transfer"

def style_transfer(
    content_image,
    style_image,
    **kwargs,
):
    # configure the received parameters
    # This function may throw lots of exceptions trying to setup parameters
    # So pass parameters carefully
    params = setup_style_transfer(kwargs)
    
    content_image = preprocess(content_image, params).to(params["device"])
    style_image = preprocess(style_image, params).to(params["device"])
    
    print_log("Building the model...", params, end="")
    network = build_model(params)
    print_log("Done", params)
    
    print_log("Configuring the params (lr, lr_decay...)...", params, end="")
    config_params(params)
    print_log("Done", params)
    
    network = train(
        network,
        content_image,
        style_image,
        params,
    )
        
    gen_image = eval(
        network,
        content_image,
        style_image,
        params,
    )
    
    return gen_image, params