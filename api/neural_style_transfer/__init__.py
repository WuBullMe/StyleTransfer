""" Style Transfer Model
    Given two images, transfer style of the second image to the first one.
    It's called Neural Style Tranfer.
    
    For more information about this algorithm, read this article in which this
    method was provided, i recommend you to read this article,
    It's very easy and understantable.
    Article: https://arxiv.org/pdf/1508.06576v2.pdf
"""

from .utils import setup_style_transfer
from .utils import preprocess
from .utils import build_model
from .utils import config_loss_layers
from .train import train
from .utils import print_log

__version__ = "1.0.0"
__name__ = "neural_style_transfer"

def style_transfer(
    content_image,
    style_image,
    **kwds,
):
    # configure the received parameters
    # This function may throw lots of exceptions trying to setup parameters
    # So pass parameters carefully
    params = setup_style_transfer(kwds)
    
    content_image = preprocess(content_image, params).to(params["device"])
    style_image = preprocess(style_image, params).to(params["device"])
    gen_image = content_image.clone().requires_grad_(True)

    print_log("Building the model...", params, end="")
    model = build_model(params)
    print_log("Done", params)
    
    print_log("Configuring the loss layers...", params, end="")
    model = config_loss_layers(model, content_image, style_image, params)
    print_log("Done", params)

    # Freeze the network in order to prevent
    # unnecessary gradient calculations
    for param in model.parameters():
        param.requires_grad = False
    
    print_log("Start training...", params)
    gen_image = train(
        model,
        gen_image,
        params,
    )
    
    print_log(params, params)
    return gen_image, params