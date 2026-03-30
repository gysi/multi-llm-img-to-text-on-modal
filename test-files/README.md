Optimize size of png
```bash
optipng -o7 [file]
pngquant --quality=75-90 --output [file]-small.png --force [file].png
```
TODO: A command that downsizes (height and width) images if they are larger than what the model can handle


Command that put file paths into a single to be referenced via k6:
```bash
find test-files/chris-bilder \
-type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.gif' \) \
| sed 's|^|test-files/chris-bilder/|' \
> imageList.txt
```
