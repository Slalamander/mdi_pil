##Not quite decent tests, but these files should run to indicate base usage is ok.

from PIL import Image
import mdi_pil as mdi

icon = "mdi:test-tube"
img = Image.new("RGBA", (100,100), None)

img = mdi.draw_mdi_icon(img, icon, icon_color="steelblue")
img.show()

img = f"./test/speaker-outline.png"

img = mdi.make_mdi_icon(img, 100, color="steelblue")
img.show()