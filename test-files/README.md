Optimize size of png
```bash
optipng -o7 [file]
pngquant --quality=75-90 --output [file]-small.png --force [file].png
```
TODO: A command that downsizes (height and width) images if they are larger than what the model can handle 
