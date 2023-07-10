# Style Transfer
- Problem: You have two images, and want to see how the first image will look like in style of the style image (briefly, transfer style of the second image to the first)

- One of the solutions: Provided in this [article](https://arxiv.org/pdf/1508.06576v2.pdf) idea to use neural network to do this. The idea is to 

# Style Transfer in Telegram
We created a Telegram bot that takes two image (content_image, style_image) and using the above idea trying to transfer the style of the second image onto first one.

# Install
You can run the bot from your computer for your own bot, just provide `API KEY` of your bot and you good to go. Also one advantage of running this code from your side is that you can tune the parameters how to transfer the style by your self.

### If you want to change the hyperparameter of the model, you should look here:
`app.py:process_images()`
```python
def process_images(img1, img2):
    gen_image, params = style_transfer(
        content_image_path=img1,
        style_image_path=img2,
        timeout_sec=60,
        logs=True,
        image_size=256,
        skip_steps=5,
    )
    img_stream = io.BytesIO()
    gen_image.save(img_stream, format='PNG')
    img_stream.seek(0)
    return img_stream, params
```

The `style_transfer` function takes content and style image path, and lots of different parameters, the main parameters you might want to change is `image_size`, `timeout_sec`, `content_weight`, `style_weight`, `tv_weight`, `epochs`. You can find full list of parameters in `model.utils:setup_style_transfer()`.

After you changed the parameters you just need to run the `app.py` file, like:
```python
python app.py
```
That all, easy right.

# Screen Shots of the bot
## Picture1
<img src="examples/screenshots/picture1.png">
<img src="examples/screenshots/result1.png">

## Picture2
<img src="examples/screenshots/picture2.png">
<img src="examples/screenshots/result2.png">

## Picture3
<img src="examples/screenshots/picture3.png">
<img src="examples/screenshots/result3.png">

## Picture4
<img src="examples/screenshots/picture4.png">
<img src="examples/screenshots/result4.png">

## Picture5
<img src="examples/screenshots/picture5.png">
<img src="examples/screenshots/result5.png">