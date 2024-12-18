# MDI PIL

This is a small library made to easily generate PIL Image objects of mdi
(Material Design Icon) icons. It also comes with a tool to convert user supplied image files into image objects that adhere to the main sizing principles of mdi icons.
There are also two additional functions, `parse_weather_icon` and `make_battery_icon`. The former returns a string with the mdi icon corresponding to a given weather condition. The latter creates an image that is similar to the icon showing the battery status in phones, with additional options like fill icons and the like. See the doc strings of those functions for how they work.

To see a project using both implementations, check out [inkBoard Designer](https://github.com/Slalamander/inkBoarddesigner). It uses PythonScreenStackManager for the actual dashboards (which is what this module was originally written for), and the UI makes heavy use of the ttkbootstrap module (and it is also where the idea for that module was born).

## Install
`pip install mdi-pil`

# Examples

Make a PIL image object with the icon "mdi:test-tube" and open a window to show it:

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

## ttkbootstrap

Version 1.1.0 comes with an optional extension to use MDI icons in tkinter interfaces. To have  functional theming, the ttkbootstrap package is used.

**installation**: `pip install mdi-pil[ttkbootstrap]` (If ttkbootstrap is not yet installed)


### Usage:

The classes return PhotoImage objects, so they are used in the same way you'd use a `PIL.ImageTk.PhotoImage`.

For more info on styling than is in the docstrings, look at the documentation for ttkbootstrap and tkinter itself.

A very rudimentary example is below, which can be run as is:

```python
from ttkbootstrap import Window, Button
from mdi_pil.ttkbootstrap_mdi import MDIIcon, MDIButton

window_size = (750,200)
root = Window(size=window_size)

KEEP = []   ##Images need to be saved somewhere to prevent garbage collecion

icon = "mdi:test-tube"
icon_size = int(window_size[1]/2)
imgTk = MDIIcon(icon, (100,100), bootstyle="info")
iconWidget = Button(root,image=imgTk, cursor="hand2", 
                        width=100, padding=-1
                        )
KEEP.append(imgTk)
iconWidget.pack()

icon = "mdi:earth"
text = "Hello World!"
button_size = (window_size[0],int(window_size[1]/2))
imgTk = MDIButton(icon, text, button_size, bootstyle="success")
buttonWidget = Button(root,image=imgTk, cursor="hand2")
KEEP.append(imgTk)
buttonWidget.pack()

root.mainloop()
```
