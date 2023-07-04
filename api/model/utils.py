import torch
from torchvision import transforms

std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)
mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)

def transform_image(image, device, image_size, norm=True):
    # transformation to apply
    transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
    ])
    
    image = transform(image).unsqueeze(0).to(device, torch.float)
    if norm:
        image = normalize(image, device)
      
    return image



def normalize(image, device):
  image = image - mean.to(device)
  image = image / std.to(device)

  return image

def denormalize(image, device):
  image = image * std.to(device)
  image = image + mean.to(device)

  return image