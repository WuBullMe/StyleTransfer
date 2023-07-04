import time
import numpy as np

from .utils import denormalize

def train(
    model,
    optimizer,
    criterion,
    content_image,
    style_image,
    gen_image,
    epochs,
    device,
    timeout_sec,
):
    start = time.time()
    for _ in range(epochs):
        gen_feat = model(gen_image)
        content_feat = model(content_image)
        style_feat = model(style_image)

        optimizer.zero_grad()
        loss = criterion(gen_feat, content_feat, style_feat)

        loss.backward()
        optimizer.step()
        
        if time.time() - start > timeout_sec:
            break
    
    gen_image = denormalize(gen_image.detach(), device)
    gen_image = gen_image.squeeze(0).permute(1, 2, 0).cpu()
    gen_image = (gen_image.numpy().clip(0, 1) * 255).astype(np.uint8)
    return gen_image