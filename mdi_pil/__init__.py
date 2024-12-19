
"""
    Helper library for drawing mdi icons on PIL images
    Main usage: mdi_pil.draw_mdi_icon

    
    Works by mapping the icon identifier (`"mdi:icon"`) to the hex values to the hex codes of the mdi webfont (materialdesignicons-webfont.ttf). The scss (_variables.scss) file is used to create this mapping.
    For those files, see: https://github.com/Templarian/MaterialDesign-Webfont (They should come with the package however).
"""
import logging
from typing import Union, Literal, Optional, Any
from types import MappingProxyType
from math import cos, sin

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops
from PIL.ImageColor import getcolor as PILgetcolor

from .constants import MDI_FONT_FILE, MDI_INDEX_FILE, MDI_WEATHER_ICONS, mdiType, ColorType

ALLOWED_MDI_IDENTIFIERS = ["mdi:"]

logger = logging.getLogger(__name__)

MDI_TRUETYPE_FONT = ImageFont.truetype(MDI_FONT_FILE.as_posix())

def rotation_matrix(coordinates:list[tuple[int,int]], angle : int, center: tuple[int,int] = (0,0)) -> list[tuple[int,int]]:
    """
    Applies a rotation matrix to the provided coordinates
    
    Paramaters
    ----------
    coordinates: list[tuple['x','y']]
        tuples of coordinates to apply to transformation to
    angle: float
        rotation angle in radians
    """
    v = []
    for (xo,yo) in coordinates:
        (x,y) = (xo-center[0],yo-center[1])
        xp = int(x*cos(angle) - y*sin(angle)) + center[0]
        yp = int(x*sin(angle) + y*cos(angle)) + center[1]
        v.append((xp,yp))
    return v

#Isolate the hex code index from the other fluff in the file
##Opening the .scss file is faster than opening a generated json file
def _build_mdi_dict() -> dict:
    "Builds a dict from the _variables.scss file"
    logger.debug("Building MDI dict")
    mdi_index_file = MDI_INDEX_FILE 
    with open(mdi_index_file,'r') as f:
        mdi_file = f.read()
    f.close()
    search_for = "$mdi-icons: ("
    index_start = mdi_file.find(search_for)
    mdi_headers = mdi_file[:index_start]
    mdi_dict = {}
    for line in mdi_headers.split(";"):
        line = line.strip().split(":")
        if len(line) > 1:
            k = line[0]
            k = k.replace("$", "")
            v = line[1]
            v = v.replace("!default","")
            v = v.replace('"','').strip()
            mdi_dict[k] = v

    mdi_icon_dict = {}
    icon_list = mdi_file[index_start + len(search_for):-2]
    def elem_splitter(s):
        return s.split(':',1)

    mdi_elements = (elem_splitter(line) for line in icon_list.split(','))
    for icon,hexcode in mdi_elements:
        icon = icon.strip()
        icon = icon[1:-1]
        hexcode = hexcode.strip()
        mdi_icon_dict[icon] = str(hexcode)

    mdi_dict["mdi-icons"] = MappingProxyType(mdi_icon_dict)

    del(mdi_file)
    del(mdi_headers)
    del(icon_list)
    del(mdi_elements)
    return MappingProxyType(mdi_dict)

mdi_dict = _build_mdi_dict()
mdi_icons = mdi_dict["mdi-icons"]
MDI_VERSION = mdi_dict['mdi-version']

#Function to get the hexcode and unicode are isolated so they can be called seperately too
def is_mdi(mdi : Any) -> bool:
    """
    Returns true if string can be parsed as an mdi icon.
    Does not check if it is an actual mdi icon. 

    Parameters
    ----------
    mdi : str
        the string to test for. Returns true if it starts with one of the allowed mdi identifiers. (See the constant ALLOWED_MDI_IDENTIFIERS)

    """
    if not isinstance(mdi, str):
        return False
    mdistr = mdi.lower()
    if len(mdistr) <= 4 or mdistr[0:4] not in ALLOWED_MDI_IDENTIFIERS:
        return False
    
    return True

def get_mdi_hex(icon : str):
    "Gets the hex code associated with the mdi icon"
    if not icon.startswith(ALLOWED_MDI_IDENTIFIERS[0]):
        raise ValueError(f"Icon strings must start with {ALLOWED_MDI_IDENTIFIERS[0]}")
    icon = icon.split(':',1)
    return mdi_icons[icon[1]]

def get_mdi_unicode(hexcode):
    "Parse the unicode of the mdi icon given by hexcode (basically, convert the hexcode string to the unicode string)"
    mdiStr = chr(int(hexcode, 16))
    return mdiStr

def parse_MDI_Icon(mdi : str) -> tuple[Literal["unicode"], Literal["hexcode"]]:
    """
    Returns the unicode and hexcode of the mdi icon requested, which can then be used in the draw_mdi_icon function

    Paramaters
    ----------
    mdi : str
        the mdi identifier

    Returns
    -------
    tuple[str,str]
        Tuple with the icon's unicode and hexcode
    """
    mdistr = mdi.lower()
    if mdistr[0:4] not in ALLOWED_MDI_IDENTIFIERS:
        logger.error(f"{mdi} is not a valid mdi icon string. Please ensure it starts with mdi:")
        return (False, False)
    
    if mdistr[4:] not in mdi_icons:
        logger.error(f"Could not find {mdistr} in the list of mdi icons. May be misspelled, or the icon may not be in the Inkboard mdi version (which is {mdi_dict['mdi-version']}).")   
        return (False, False)
    else:
        hexcode = mdi_icons[mdistr[4:]]
        unicode = chr(int(hexcode, 16))
        return (unicode,hexcode)

def _get_Color(color : Union[str,tuple], colorMode:str) -> Union[tuple]:
    "Converts a color, if possible, into the provided colorMode. Helper function"
    if color == None:
        colorList = [0]*len(colorMode)
        return tuple(colorList)
    if isinstance(color,int):
        if color < 0:
            color = 0
        elif color > 255:
            color = 255
        
        colorList = [color]*len(colorMode)
        if "A" in colorMode:
            colorList[-1] = 255
        return tuple(colorList)
    
    if isinstance(color,(list,tuple)):
        if len(color) == len(colorMode):
            return tuple(color)
        else:
            color = tuple(color)
            colorList = [0]*len(colorMode)

            ##This line plus the alpha channel at the end should take care of BW colors
            if len(color) in [1,2]:
                colorList[0:len(colorMode)] = [color[0]] * len(colorMode)
            else:
                ##Means color is RGB or RGBA
                if "RGB" in colorMode:
                    colorList[0:3] = color[0:3]
                else:
                    r, g, b = color[0], color[1], color[2]
                    colorList[0] = int( 0.2989 * r + 0.5870 * g + 0.1140 * b)
            if "A" in colorMode:
                ##Setting the alpha channel to be non transparent if not specified, or to the predefined value
                colorList[-1] = color[-1] if len(color) in [2,4] else 255
            
            return tuple(colorList)
    
    if isinstance(color, str):       
        try:
            colorTup = PILgetcolor(color,colorMode)
        except:
            logger.error(f"Could not recognise {color} as a valid color. Returning black")
            return PILgetcolor("black",colorMode)
        else:
            if isinstance(colorTup,int): 
                colorTup = tuple([colorTup])
            return colorTup

    #Code should not get here (And can't, apparently), but leaving it just in case.
    logger.error(f"Something went wrong converting {color} to a color value, returning 0 (black)")
    return 0

def invert_Color(color : Union[str,tuple], colorMode):
    "Inverts a color. Does not perform checks for validity."
    
    ##Convert the color into a tuple
    color = _get_Color(color,colorMode)
    invCol = list(map(lambda c: 255 - c, color))
    if "A" in colorMode:
        invCol[-1] = color[-1]
    
    return tuple(invCol)

def invert_Image(img : Image.Image) -> Image.Image:
    "Invert the provided image. Also supports inverting of images with alpha channels (transparancy is not inverted)"
    img = img.copy()
    if "A" in img.mode:
        alpha = img.getchannel("A")
        img = ImageChops.invert(img)
        img.putalpha(alpha)
    else:
        img = ImageOps.invert(img)
    return img

def draw_mdi_icon(Pillowimg : Image.Image, mdi : Union[tuple,str], 
                icon_coords : tuple[Literal["x"],Literal["y"]]=None, icon_size:int=None, icon_color : Union[str,tuple] ="black", iconDraw: Optional[ImageDraw.ImageDraw] = None) -> Image.Image:
    """
    Draws the provided mdi icon onto Pillowimg.

    Parameters
    ----------
    Pillowimg : Image.Image
        The image to draw upon
    mdi : Union[tuple,str]
        string for the mdi, or a tuple containing data of the mdi icon  (can be gotten by calling `parse_MDI_Icon`)
    icon_coords : tuple[Literal[&quot;x&quot;],Literal[&quot;y&quot;]], optional
        center coordinates of icon as an (x,y) tuple, by default None
    icon_size : int, optional
        size of the icon (including padding) in pixels. If left at None, will use the image's size (maximum size to have it fit within Pillowimg). by default None
    icon_color : Union[str,tuple], optional
        icon color, needs to be a value usable by PIL, by default "black"
    iconDraw : Optional[ImageDraw.ImageDraw], optional
        optional ImageDraw object. If provided, the function will not generate a new ImageDraw

    Returns
    -------
    Image.Image
        Image with the mdi icon drawn on it.
    """
    if isinstance(mdi,tuple):
        mdi_tuple = mdi
    elif isinstance(mdi,str):
        mdi_tuple = parse_MDI_Icon(mdi)
        
        if not mdi_tuple[0]:
            raise ValueError(f"{mdi} is not found as a valid mdi icon.")
    else:
        raise TypeError(f"MDI must be of type str or tuple, {mdi} with type {type(mdi)} is invalid.")

    fill = _get_Color(icon_color, Pillowimg.mode)
    
    if iconDraw == None:
        iconDraw = ImageDraw.Draw(Pillowimg)

    img_size = Pillowimg.size

    ##If None, shouldn't font size be the y coordinate by default? --> no it has to fit in a box
    font_size = min(img_size) if icon_size == None else int(icon_size)
    mdi_font = MDI_TRUETYPE_FONT.font_variant(size=font_size)
    mdi_str = (mdi_tuple[0])
    
    if icon_coords == None:
        icon_coords = (img_size[0]/2, img_size[1]/2)

    iconDraw.text(
        icon_coords,
        mdi_str,
        anchor="mm",
        font=mdi_font,
        fill = fill)
    return Pillowimg

def make_mdi_icon(img : Union[Image.Image,str], size : int = 500, color : ColorType = None) -> Image.Image:
    """
    Generates an image that tries to mimick the sizing of mdi icons as much as possible.
    

    Parameters
    ----------
    img : Union[Image.Image,str]
        Image to convert. Can be a PIL image instance or a string pointing to an image file.
    size : int, optional
        Size of the sides of the returned image in pixels, by default 500 (Any returned image is square)
    color : ColorType, optional
        Color of the returned icon. Any pixel that does not have an alpha channel of 0 will have this color applied to it. By default None, which means the colors are not changed.

    Returns
    -------
    Image.Image
        The mdi-like icon image.
    """

    if isinstance(img, Image.Image):
        iconImg = img
    else:
        iconImg = Image.open(img)
    ##Convert it here already to prevent problems with pasting etc. Cause like this is is guaranteed to have an alpha channel
    if iconImg.mode != "RGBA": iconImg = iconImg.convert("RGBA")
    ##MDI icons have a live area of 20dp, and padding of 2dp on both sides
    ##So for resizing: grab min size of the loaded img, take that as square size
    ##Resize the icon. Size must be ~20/24 of the square (0.83); Image.thumbnail should make the image fit within the size
    ##Determine the origin of the square within the loaded img
    
    ##This way, any alpha channel around the icon is automatically removed
    iconImg = iconImg.crop(iconImg.getbbox())
    liveArea = 20/24 ##The ratio of the area where icons are as defined by mdi design guide
    thumbSize = int(size*liveArea)
    iconImg = ImageOps.contain(iconImg,(thumbSize,thumbSize))
    iconImg = ImageOps.pad(iconImg,(size,size))
    
    if color != None:
        icondraw = ImageDraw.Draw(iconImg)
        icondraw.bitmap((0,0),iconImg.getchannel("A"),color)

    return iconImg

def parse_weather_icon(condition,night:bool=False) -> str:
    ##See here https://developers.home-assistant.io/docs/core/entity/weather#recommended-values-for-state-and-condition
    """
    Returns name of the mdi icon corresponding to the given weather condition (roughly). See constants.MDI_WEATHER_ICONS for the mapping of icons to conditions.
    
    Parameters
    -----------
    condition (str): 
        the weather condition to look for
    night (bool): 
        Will look for the condition in the icons under the night key of the conditionDict. If not found in there, will look in the daytime conditions, otherwise go to default.
    """

    ##Maybe add a check to see if it returns a valid mdi icon
    prefix:str="mdi:weather-"
    conditionDict = MDI_WEATHER_ICONS

    
    if night:
        icon_id = conditionDict["night"].get(condition,conditionDict["day"].get(condition,"default"))
    else:
        icon_id = conditionDict["day"].get(condition,"default")
    
    if icon_id == "default":
        logger.warning(f"Could not find weather condition {condition} in the condition day keys, returning default value")
        icon_id = conditionDict["default"]

    return f"{prefix}{icon_id}"

def make_battery_icon(charge : int, fillIcon : Optional[mdiType] = None, color : Union[str,tuple[int,int,int,int]] = "black", size : int = 500,
                    style : Literal["filled", "bars", ] = "filled", orientation : Literal["ver","vertical","hor","horizontal"] = "ver", fillRotation : int = 0) -> Image.Image:
    """
    Makes a battery icon from the mdi:battery icons. 
    Optionally fill it with another mdi icon, which will be used as an alpha mask on the battery icon itself, and pasted where the icon is not filled.
    (If that is not clear, just call the function with charge at 50 and look at the returned image.)

    Parameters
    ----------
    charge : int
        charge percentage, 0-100.
    fillIcon : Optional[mdiType], optional
        Icon to show in the inside of the battery, by default None
    color : ColorType, optional
        Valid color value for PIL (string or 4 tuple), by default "black"
    size : int, optional
        Size of the icon sides (A square image is always returned). , by default 500
    orientation : Literal[&quot;ver&quot;,&quot;vertical&quot;,&quot;hor&quot;,&quot;horizontal&quot;], optional
        orientation of the battery, by default "ver"
    fillRotation : int, optional
        rotation of the fillIcon, in degrees, by default 0

    Returns
    -------
    Image.Image
        The battery icon image
    """
    
    ##Trial and error; w,h is about the size of the inner section of the empty battery
    w = int(size*0.3)
    h = int(size*0.57)
    size = (size,size)
    img = Image.new("RGBA",size)
    
    if style == "filled":
        level_rounded = round(charge/10)*10
        if level_rounded == 0:
            level_rounded = "outline"
        elif level_rounded > 100:
            level_rounded = 100
        if level_rounded == 100:
            batteryIcon = f"mdi:battery"
        else:
            batteryIcon = f"mdi:battery-{level_rounded}"
    elif style == "bars":
        if charge <= 5:
            batteryIcon = "mdi:battery-outline"
        elif charge <= 35:
            batteryIcon = "mdi:battery-low"
        elif charge <= 65:
            batteryIcon = "mdi:battery-medium"
        elif charge <= 95:
            batteryIcon = "mdi:battery-high"
        else:
            batteryIcon = "mdi:battery"
    else:
        raise ValueError(f"Invalid battery style: {style}")
    
    img = draw_mdi_icon(img,batteryIcon, icon_color=color)

    if fillIcon != None:
        fill = draw_mdi_icon(Image.new("RGBA",size),fillIcon,icon_color=color)
        fill = fill.crop(fill.getbbox())
        if fillRotation != 0:
            fill = fill.rotate(fillRotation,expand=True)
        fill = ImageOps.contain(fill,(w,h))

        ##Applies the inverted alpha channel, which means only the fill icon is invisible
        m = ImageOps.invert(fill.getchannel("A"))
        imgph = Image.new("LA",fill.size)
        imgph.putalpha(m)

        ##Getting the battery mask
        m = ImageOps.invert(img.getchannel("A"))

        ##Again, found out via trial and error; t is the top of the inner battery space, b the bottom
        t = int(img.height*0.26)
        b = t + h
        coords = (int((img.width-w)/2),int((b+t-fill.height)/2))
        img.paste(imgph,coords,mask=fill.getchannel("A"))

        ##To correctly apply the battery mask, the fill icon needs to be the same size as the mask.
        ##So crop out the area where the icon will be pasted
        cropbox = (coords[0],coords[1],coords[0]+fill.width,coords[1]+fill.height)
        m = m.crop(cropbox)
        img.paste(fill,cropbox,m)

    if "hor" in orientation:
        img = img.rotate(-90)
    
    return img