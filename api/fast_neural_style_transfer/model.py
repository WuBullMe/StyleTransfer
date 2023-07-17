from torch.nn import Module, Sequential, Conv2d, ReflectionPad2d
import torch.nn.functional as F

class ConvBlock(Module):
    def __init__(self, in_channels, out_channels, kernel_size, activation=True, max_pool=False, upsample=False):
        super().__init__()

        self.activation = activation
        self.max_pool = max_pool
        self.upsample = upsample
        self.conv = Sequential(ReflectionPad2d(kernel_size // 2),
                               Conv2d(in_channels, out_channels, kernel_size))

    def forward(self, x):
        conv = self.conv(x)
        if self.activation:
            conv = F.relu(conv)
        if self.max_pool:
            conv = F.max_pool2d(conv, kernel_size=2, stride=2, ceil_mode=True)
        elif self.upsample:
            conv = F.interpolate(conv, scale_factor=2)
        return conv


class Network(Module):
    def __init__(self):
        super().__init__()

        # Encoder
        self.encoder = Sequential(Sequential(Conv2d(3, 3, kernel_size=1),
                                             ConvBlock(3, 64, kernel_size=3)),
                                  Sequential(ConvBlock(64, 64, kernel_size=3, max_pool=True),
                                             ConvBlock(64, 128, kernel_size=3)),
                                  Sequential(ConvBlock(128, 128, kernel_size=3, max_pool=True),
                                             ConvBlock(128, 256, kernel_size=3)),
                                  Sequential(ConvBlock(256, 256, kernel_size=3),
                                             ConvBlock(256, 256, kernel_size=3),
                                             ConvBlock(256, 256, kernel_size=3, max_pool=True),
                                             ConvBlock(256, 512, kernel_size=3)))

        # Decoder
        self.decoder = Sequential(ConvBlock(512, 256, kernel_size=3, upsample=True),
                                  ConvBlock(256, 256, kernel_size=3),
                                  ConvBlock(256, 256, kernel_size=3),
                                  ConvBlock(256, 256, kernel_size=3),
                                  ConvBlock(256, 128, kernel_size=3, upsample=True),
                                  ConvBlock(128, 128, kernel_size=3),
                                  ConvBlock(128, 64, kernel_size=3, upsample=True),
                                  ConvBlock(64, 64, kernel_size=3),
                                  ConvBlock(64, 3, kernel_size=3, activation=False))

        # Freeze Encoder Parameters
        for parameter in self.encoder.parameters():
            parameter.requires_grad = False

    # Get Features From All Encoder Layers
    def get_all_encoder_features(self, input):
        features = [input]
        for i in range(4):
            features.append(self.encoder[i](features[-1]))
        return features[1:]

    # Apply Adaptive Instance Normalization
    def adain(self, content_feats, style_feats):
        size = content_feats.size()
        style_mean, style_std = calculate_mean_std(style_feats)
        content_mean, content_std = calculate_mean_std(content_feats)
        normalized_feats = (content_feats - content_mean.expand(size)) / content_std.expand(size)
        return normalized_feats * style_std.expand(size) + style_mean.expand(size)

    # Calculate Content Loss
    def content_loss(self, input, target):
        return F.mse_loss(input, target)

    # Calculate Style Loss
    def style_loss(self, input, target):
        input_mean, input_std = calculate_mean_std(input)
        target_mean, target_std = calculate_mean_std(target)
        return F.mse_loss(input_mean, target_mean) + F.mse_loss(input_std, target_std)

    def forward(self, content, style, alpha=1):
        assert 0 <= alpha <= 1
        content_feats = self.encoder(content)
        style_feats = self.get_all_encoder_features(style)
        stylized_feats = self.adain(content_feats, style_feats[-1])
        stylized_feats = alpha * stylized_feats + (1 - alpha) * content_feats

        generated_stylization = self.decoder(stylized_feats)
        generated_stylization_feats = self.get_all_encoder_features(generated_stylization)

        content_loss = self.content_loss(generated_stylization_feats[-1], stylized_feats)
        style_loss = self.style_loss(generated_stylization_feats[0], style_feats[0])
        for i in range(1, 4):
            style_loss += self.style_loss(generated_stylization_feats[i], style_feats[i])
        return content_loss, style_loss
    
    
def calculate_mean_std(features, eps=1e-5):
    size = features.size()
    N, C = size[:2]
    features_var = features.view(N, C, -1).var(dim=2) + eps
    features_std = features_var.sqrt().view(N, C, 1, 1)
    features_mean = features.view(N, C, -1).mean(dim=2).view(N, C, 1, 1)
    return features_mean, features_std