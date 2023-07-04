import torch

class ContentStyleLoss(torch.nn.Module):
    def __init__(
            self,
            alpha,
            beta,
            all_conv, 
            content_conv,
            style_conv,
        ):
        super(ContentStyleLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.all_conv = all_conv
        self.content_conv = content_conv
        self.style_conv = style_conv
        
        
    def content_loss(self, gen_feat, content_feat):
        return torch.mean((gen_feat - content_feat) ** 2)
    
    def style_loss(self, gen_feat, style_feat):
        batch_size, channel, height, width = gen_feat.shape

        G = torch.mm(
            gen_feat.view(channel, height * width),
            gen_feat.view(channel, height * width).t()
        )

        A = torch.mm(
            style_feat.view(channel, height * width),
            style_feat.view(channel, height * width).t()
        )
        return torch.mean((G - A) ** 2)
    
    def forward(self, gen_feat, content_feat, style_feat):
        style_loss_total = 0
        content_loss_total = 0
        for i in range(len(self.all_conv)):
            if self.all_conv[i] in self.content_conv:
                content_loss_total += self.content_loss(gen_feat[i], content_feat[i])

            if self.all_conv[i] in self.style_conv:
                style_loss_total += self.style_loss(gen_feat[i], style_feat[i])

        return (self.alpha * content_loss_total + self.beta * style_loss_total)

