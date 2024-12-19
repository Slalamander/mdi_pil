"Provides some classes that allow usage with the ttkbootstrap package, to make icons and widgets that can change color along with theme changes. Use in the same way that ImageTk.IconImage is used."

import re

from PIL import ImageTk, Image, ImageFont, ImageDraw

from ttkbootstrap import constants as const
from ttkbootstrap.style import Keywords, Bootstyle, StyleBuilderTTK
from ttkbootstrap.publisher import Publisher, Channel

from . import *


class PhotoIcon(ImageTk.PhotoImage):
    """PhotoImage that can be used as an icon in ttkbootstrap.

    Allows for changing the color via changing both the bootstyle parameter as well as changing the theme. Keep in mind the former may be slow as it is not the intended use.
    Alpha channel is preserved during color changes, at any other point the color is put. Icons cannot be changed, just the color.

    Bootstyles _should_ fully work as they do for ttkbootstrap.
    Internally, they use the TIcon style by default, with the color being gotten from the 'icon' of the style.
    I.e. using style.configure(style='TIcon', icon="purple"). 

    
    Parameters
    ----------
    image : _type_, optional
        The image to use as an icon, by default None (Not sure how that will work though, generally pass an image to this)
    size : tuple[int,int], optional
        Size tuple for the PhotoImage, by default None
    bootstyle : BootstrapKeywords, optional
        The bootstyle to use, by default "primary"
    style : str, optional
        ttk style identifier. By default None. If not None, overwrites the bootstyle value.
    """

    _last_id = 0
    _basestyle = "TIcon"

    def winfo_class(self):
        #Placeholder to function with the ttkbootstrap api. Does not interface with tkinter
        return "Icon"

    def __init__(self, image = None, size: tuple[int,int] = None, bootstyle: Keywords.COLORS = "primary", style: str = None, **kw):

        super().__init__(image, size, **kw)
        
        self._img: Image.Image = image
        self.bootstyle = bootstyle
        self._name = f"{self.__class__.__name__}::{self._last_id}"
        self.__class__._last_id += 1

        self._style = style

        Publisher.subscribe(self._name, self._change_img_style, Channel.STD)
        self._change_img_style()

    def __str__(self) -> str:
        """
        Get the Tkinter photo image identifier.  This method is automatically
        called by Tkinter whenever a PhotoImage object is passed to a Tkinter
        method.

        :return: A Tkinter photo image identifier (a string).
        """
        return super().__str__()

    @property
    def bootstyle(self) -> str:
        return self._bootstyle
    
    @bootstyle.setter
    def bootstyle(self, value: str):
        self._bootstyle = value

    @property
    def style(self) -> str:
        return self._style
    
    @style.setter
    def style(self, value):
        self._style = value

    def _get_ttk_style(self):
        "Gets the value of the ttk style associated with the PhotoIcon"
        if self.style != None:
            return self.style
        else:
            return Bootstyle.update_ttk_widget_style(self,self.bootstyle)

    def _get_color(self):
        ttk_style = self._get_ttk_style()
        value = self.tk.call(
            "ttk::style", "lookup", ttk_style, "-%s" % "icon", None, None
        )
        if not value: return "black" ##Failsafe in case a color does not exist
        return value

    def _change_img_style(self, *args):
        
        img = self._img
        new_color = self._get_color()
        new_img = Image.new(img.mode,img.size, new_color)
        new_img.putalpha(img.getchannel("A"))
        self.paste(new_img)

    @staticmethod
    def create_icon_style(self: StyleBuilderTTK, colorname=const.DEFAULT):

        STYLE = PhotoIcon._basestyle

        if any([colorname == const.DEFAULT, colorname == ""]):
            ttkstyle = STYLE
            icon = self.colors.primary
        else:
            ttkstyle = f"{colorname}.{STYLE}"
            icon = self.colors.get(colorname)
        
        self.style._build_configure(
                ttkstyle,
                icon=icon
            )
        self.style._register_ttkstyle(ttkstyle)

class MDIIcon(PhotoIcon):
    """Creates MDI Icons that can follow a ttkbootstrap theme

    Parameters
    ----------
    icon : mdiType
        mdi icon to use (pass as "mdi:my-icon")
    size : tuple[int,int]
        The size of the icon
    """   

    def __init__(self, icon: mdiType, size: tuple[int,int], bootstyle: Keywords.COLORS = "primary", **kw):
        
        img = Image.new("RGBA", size=size, color=None)
        img = draw_mdi_icon(img,icon, icon_color="black")
        
        super().__init__(img, None, bootstyle, **kw)

class MDIButton(PhotoIcon):
    """A photoimage with an mdi icon and text. 

    Similar in use to the PhotoIcon, but additionally allows styling of the textcolor.
    To change the style, use identifier TIconButton. icon is the icon color, foreground is the text color.

    I.e. using style.configure(style='TIcon', icon="purple", foreground="green"). 

    Parameters
    ----------
    icon : mdiType
        mdi icon to use
    text : str
        Text to show on the button
    size : tuple[int,int]
        Size of the image to be generated, in pixels
    font_file : str, optional
        Optional font file to use, otherwise uses the default font, by default None
    icon_size : float, optional
        Size of the icon, defaults to using the entire height, by default None 
    font_size : float, optional
        Font size, defaults to using the entire height, by default None
    icon_margin : tuple[int,int], optional
        Margins of the icon. Either left-right are the same (one integer), by default 0
        Or a (left, right) tuple is passed.
    """

    _basestyle = "TIconbutton"

    ##Will allow for separate styling of the icon and the image, and simply regenerate the images.
    ##Idk how well they'll behave 

    def __init__(self, icon: mdiType, text: str, 
                size: tuple[int,int], font_file: str = None,
                icon_size: int = None, font_size: int = None,
                icon_margin: tuple[int,int] = 0,
                **kw):


        self.__size = size
        w,h = self.__size

        if isinstance(icon_margin,int):
            icon_margin = (icon_margin,icon_margin)

        if icon_size == None: icon_size = h
        if font_size == None: font_size = h

        iconCoords = (int(icon_size/2) + icon_margin[0] ,int(h/2))
        textCoords = (icon_margin[0] + icon_size + icon_margin[1],
                    iconCoords[1])

        self.__split_coords = icon_margin[0] + icon_size

        img = Image.new("RGBA", size=(w,h))
        draw = ImageDraw.Draw(img)
        img = draw_mdi_icon(img, icon, icon_size=icon_size, icon_coords=iconCoords, icon_color="black", iconDraw=draw)

        if font_file == None:
            loaded_font = ImageFont.load_default(font_size)
        else:
            loaded_font = ImageFont.truetype(font_file, size=font_size)
        draw.text(textCoords, text=text, anchor="lm",
                        font=loaded_font, fill="black")

        super().__init__(img, size, **kw)

    def _get_color(self, ttk_style, component):

        value = self.tk.call(
            "ttk::style", "lookup", ttk_style, "-%s" % component, None, None
        )
        if not value: return "black" ##Failsafe in case a color does not exist
        return value

    def winfo_class(self):
        return "IconButton"

    def _change_img_style(self, *args):
        
        ttk_style = self._get_ttk_style()
        img: Image.Image = self._img
        new_img = Image.new(img.mode,img.size, None)

        text_color = self._get_color(ttk_style, "foreground")
        icon_color = self._get_color(ttk_style, "icon")

        old_icon = img.crop((0,0,self.__split_coords,img.height))
        new_icon = Image.new(img.mode,old_icon.size, icon_color)
        new_icon.putalpha(old_icon.getchannel("A"))
        
        old_text = img.crop((self.__split_coords, 0, img.width, img.height))
        
        new_text = Image.new(img.mode, old_text.size, text_color)
        new_text.putalpha(old_text.getchannel("A"))

        new_img.paste(new_icon)
        new_img.paste(new_text, (self.__split_coords,0))
        self.paste(new_img)
        return
    
    @staticmethod
    def create_iconbutton_style(self: StyleBuilderTTK, colorname=const.DEFAULT):

        STYLE = MDIButton._basestyle

        if any([colorname == const.DEFAULT, colorname == ""]):
            ttkstyle = STYLE
            icon = self.colors.primary
            foreground = self.colors.fg
        else:
            ttkstyle = f"{colorname}.{STYLE}"
            icon = self.colors.get(colorname)
            foreground = self.colors.fg

        if colorname.lower() in {"danger", "warning","success"}:
            foreground = icon

        self.style._build_configure(
                ttkstyle,
                icon=icon,
                foreground=foreground
            )
        self.style._register_ttkstyle(ttkstyle)


StyleBuilderTTK.create_iconbutton_style = MDIButton.create_iconbutton_style
StyleBuilderTTK.create_icon_style = PhotoIcon.create_icon_style

Keywords.CLASSES.extend(["iconbutton","icon"])
Keywords.CLASS_PATTERN = re.compile("|".join(Keywords.CLASSES))

__all__ = [
    "PhotoIcon",
    "MDIIcon",
    "MDIButton"
]