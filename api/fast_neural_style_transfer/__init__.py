"""Style Transfer Model
    Given two images, transfer style of the second image to the first one.
    It's called Neural Style Tranfer.

    For more information about this algorithm, read this article in which this
    method was provided, i recommend you to read this article,
    Article: https://arxiv.org/pdf/1703.06868.pdf
"""

from copy import deepcopy
import time

from .utils import setup_style_transfer
from .utils import preprocess
from .utils import build_model
from .utils import print_log
from .train import train
from .train import evaluate

__version__ = "1.0.0"
__name__ = "fast_neural_style_transfer"

model = None
last_trained = None

def style_transfer(
    content_image,
    style_image,
    **kwds,
):
    # configure the received parameters
    # This function may throw lots of exceptions trying to setup parameters
    # So pass parameters carefully
    params = setup_style_transfer(kwds)
    
    # measure preprocess time
    content_image = preprocess(content_image, params).to(params["device"])
    style_image = preprocess(style_image, params).to(params["device"])
    
    global model
    if model is None:
        print_log("Building the model...", params, end="")
        model = build_model(params)
        print_log("Done", params)
    
    # add some model params
    params['lr'] = 1e-4
    params['lr_decay'] = 5e-5
    
    global last_trained
    if params['train'] or last_trained is None:
        # train the network
        network = deepcopy(model)
        network = train(
            network,
            content_image,
            style_image,
            params,
        )
        last_trained = network
    else:
        network = last_trained

    # eval the network
    gen_image = evaluate(
        network,
        content_image,
        style_image,
        params,
    )
    
    return gen_image, params
