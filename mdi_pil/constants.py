
from pathlib import Path
from typing import TypeVar, Union

__version__ = "1.1.6"

MDI_FONT_FILE = "materialdesignicons-webfont.ttf"
MDI_INDEX_FILE = "_variables.scss"

MDI_FONT_FILE = Path(__file__).resolve().with_name(MDI_FONT_FILE)
MDI_INDEX_FILE = Path(__file__).resolve().with_name(MDI_INDEX_FILE)

MDI_WEATHER_ICONS : dict = {"default": "cloudy",
        "day": {
            "clear-night": "night",
            'cloudy':"cloudy",
            "exceptional": "cloudy-alert",
            'fog': "fog",
            'hail': "hail",
            'lightning': 'lightning',
            "lightning-rainy": "lightning-rainy",
            "partlycloudy": "partly-cloudy",
            "pouring": "pouring",
            'rainy': "rainy",
            "snowy": "snowy",
            "snowy-rainy": "snowy-rainy",
            "sunny": "sunny",
            "windy": "windy",
            "windy-variant": "windy-variant",

            ##Icons not in the recommended conditions, but present as mdi icons. See https://pictogrammers.com/library/mdi/category/weather/
            'hazy': "hazy",
            "hurricane": "hurricane",
            'dust': "dust",
            "partly-lightning": "partly-lightning",
            "partly-rainy": "partly-rainy",
            "partly-snowy": "partly-snowy",
            "partly-snowy-rainy": "partly-snowy-rainy",             
            "snowy-heavy": "snowy-heavy",
            "tornado": "tornado"
            },
        "night": {
            'cloudy': "night-partly-cloudy",
            "partlycloudy": "night-partly-cloudy",
            "sunny": "night",
            "clear-night": "night"
            }}
"Dict linking forecast conditions to mdi icons"

mdiType = TypeVar("mdi:icon", bound=str)
"type hint for mdi icons"

ColorType = Union[str,int,list,
            tuple[TypeVar('L'),TypeVar('A')], ##LA type
            tuple[TypeVar('R'),TypeVar('G'),TypeVar('B')], ##RGB type
            tuple[TypeVar('R'),TypeVar('G'),TypeVar('B'),TypeVar('A')] ##RGBA type
            ]
"Types for valid colors in the supported color modes. Very broad, generally call tools.is_valid_color for actual validation."
