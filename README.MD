# MDI PIL

This is a small library made to easily generate PIL Image objects of mdi
(Material Design Icon) icons. It also comes with a tool to convert user supplied image files into image objects that adhere to the main sizing principles of mdi icons.
There are also two additional functions, `parse_weather_icon` and `make_battery_icon`. The former returns a string with the mdi icon corresponding to a given weather condition. The latter creates an image that is similar to the icon showing the battery status in phones, with additional options like fill icons and the like. See the doc strings of those functions for how they work.


# Examples

Make an PIL image object of the icon "mdi:test-tube" and open a window to show it:

```
from PIL import Image
import mdi_pil as mdi

icon = "mdi:test-tube"
img = Image.new("RGBA", (100,100), None)

img = mdi.draw_mdi_icon(img, icon, icon_color="steelblue")
img.show()
```

Convert the image file "speaker-outline.png" into an mdi-like icon:

```
from PIL import Image
import mdi_pil as mdi

img = "speaker-outline.png"

img = mdi.make_mdi_icon(img, 100, color="steelblue")
img.show()
```