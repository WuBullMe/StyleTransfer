# check if parameters are correctly passed to the model

def image_size_(image_size):
    supported_types = (int, tuple, list)
    allowed_range = (2, 2**10)
    _check_type(image_size, supported_types, "image_size")
    
    if type(image_size) is int:
        image_size = (image_size, image_size)
    
    if len(image_size) != 2:
        raise ValueError(f"Expected image_length to be 2, but given {len(image_size)}")
    
    _check_range(image_size[0], allowed_range, "image_size[0]")
    _check_range(image_size[1], allowed_range, "image_size[1]")
    
    return image_size


def timeout_sec_(timeout_sec):
    supported_types = (int,)
    allowed_range = (0, 60)
    _check_type(timeout_sec, supported_types, "timeout_sec")
    _check_range(timeout_sec, allowed_range, "timeout_sec")
    
    return timeout_sec


def device_(device):
    # todo: find a way to check if given device is correct is not
    return device

def epochs_(epochs):
    supported_types = (int,)
    allowed_range = (0, 5000)
    _check_type(epochs, supported_types, "epochs")
    _check_range(epochs, allowed_range, "epochs")
    
    return epochs

def content_weight_(content_weight):
    supported_types = (int, float)
    allowed_range = (1e-5, 1e5)
    _check_type(content_weight, supported_types, "content_weight")
    _check_range(content_weight, allowed_range, "content_weight")
    
    return content_weight

def style_weight_(style_weight):
    supported_types = (int, float)
    allowed_range = (1e-5, 1e5)
    _check_type(style_weight, supported_types, "style_weight")
    _check_range(style_weight, allowed_range, "style_weight")
    
    return style_weight

def alpha_(alpha):
    supported_types = (int, float)
    allowed_range = (0, 1)
    _check_type(alpha, supported_types, "alpha")
    _check_range(alpha, allowed_range, "alpha")
    
    return alpha

def logs_(logs):
    supported_types = (bool,)
    _check_type(logs, supported_types, "logs")
    
    return logs

def train_(train):
    supported_types = (bool,)
    _check_type(train, supported_types, "train")
    
    return train

def save_network_(save_network_):
    supported_types = (bool,)
    _check_type(save_network_, supported_types, "save_network_")
    
    return save_network_

def from_path_(from_path):
    supported_types = (bool,)
    _check_type(from_path, supported_types, "from_path")
    
    return from_path


def _check_allowed(x, allowed, msg):
    if x not in allowed:
        raise ValueError(f"{msg} is not allowed, you can use these: {allowed}")

def _check_range(x, allowed_range, param):
    if not(allowed_range[0] <= x <= allowed_range[1]):
        raise ValueError(f"{param} is out of range, given {x}, but allowed range: {allowed_range}")

def _check_type(x, supp_types, param):
    if type(x) not in supp_types:
        raise ValueError(f"Unsupported type for {param}, supported types are: {supp_types}")
