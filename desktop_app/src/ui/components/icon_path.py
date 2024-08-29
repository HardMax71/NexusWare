from enum import Enum


class IconPath(str, Enum):
    # ":" stuff is a Qt resource path
    APP_ICON: str = "icons:app_icon.png"

    REFRESH: str = "icons:refresh.png"
    BARCODE: str = "icons:barcode.png"
    SAVE: str = "icons:save.png"

    EYE_VIEW: str = "icons:eye_view.png"
    VIEW: str = "icons:view.png"

    BELL: str = "icons:bell.png"
    BELL_UNREAD: str = "icons:bell_unread.png"

    EDIT: str = "icons:edit.png"
    DELETE: str = "icons:delete.png"
    ADJUST: str = "icons:adjust.png"
    SHIP: str = "icons:ship.png"
    TRACK: str = "icons:track.png"
    LABEL: str = "icons:label.png"

    YES: str = "icons:yes.png"
    NO: str = "icons:no.png"

    OFFLINE: str = "icons:offline.png"

    SYNC: str = "icons:sync.png"

    SEARCH: str = "icons:search.png"

    PLUS: str = "icons:plus.png"
