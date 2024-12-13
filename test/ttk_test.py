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