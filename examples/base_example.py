##Small example for generating images with MDI icons, and converting your own images to an icon rougly matched to mdi specs

from PIL import Image
import mdi_pil as mdi

icon = "mdi:test-tube"
img = Image.new("RGBA", (100,100), None)

img = mdi.draw_mdi_icon(img, icon, icon_color="steelblue")
img.show()

img = f"./speaker-outline.png"

img = mdi.make_mdi_icon(img, 100, color="steelblue")
img.show()