from enum import Enum


class IconPath(Enum):
    REFRESH: str = "icons:refresh.png"  # ":" stuff is a Qt resource path
    BARCODE: str = "icons:barcode.png"
    SAVE: str = "icons:save.png"

    EYE_VIEW: str = "icons:eye_view.png"

    VIEW: str = "icons:view.png"
    EDIT: str = "icons:edit.png"
    DELETE: str = "icons:delete.png"
    ADJUST: str = "icons:adjust.png"
    SHIP: str = "icons:ship.png"
    TRACK: str = "icons:track.png"
    LABEL: str = "icons:label.png"

    OFFLINE: str = "icons:offline.png"

    SYNC: str = "icons:sync.png"

    SEARCH: str = "icons:search.png"

    PLUS: str = "icons:plus.png"
