from cms.constants import LEFT
from cms.toolbar.items import BaseItem, SubMenu, ToolbarAPIMixin
from django.utils.encoding import force_str


class SideframeItemCustom(BaseItem):
    template = "toolbar/items/item_sideframe.html"

    def __init__(
        self,
        name,
        url,
        active=False,
        disabled=False,
        extra_classes=None,
        on_close=None,
        side=LEFT,
        led=False,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        super().__init__(side)
        self.name = force_str(name)
        self.url = url
        self.active = active
        self.disabled = disabled
        self.extra_classes = extra_classes or []
        self.on_close = on_close
        self.led = led
        self.to_check = to_check
        self.ok_condition = ok_condition
        self.warning_condition = warning_condition
        self.error_condition = error_condition

    def __repr__(self):
        return "<SideframeItem:%s>" % force_str(self.name)

    def get_context(self):
        return {
            "url": self.url,
            "name": self.name,
            "active": self.active,
            "disabled": self.disabled,
            "extra_classes": self.extra_classes,
            "on_close": self.on_close,
            "led": self.led,
            "to_check": self.to_check,
            "ok_condition": self.ok_condition,
            "warning_condition": self.warning_condition,
            "error_condition": self.error_condition,
        }


class LinkItemCustom(BaseItem):
    template = "toolbar/items/item_link.html"

    def __init__(
        self,
        name,
        url,
        active=False,
        disabled=False,
        extra_classes=None,
        side=LEFT,
        target_blank=False,
        led=False,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        super().__init__(side)
        self.name = name
        self.url = url
        self.active = active
        self.disabled = disabled
        self.extra_classes = extra_classes or []
        self.target_blank = target_blank
        self.led = led
        self.to_check = to_check
        self.ok_condition = ok_condition
        self.warning_condition = warning_condition
        self.error_condition = error_condition

    def __repr__(self):
        return "<LinkItem:%s>" % force_str(self.name)

    def get_context(self):
        return {
            "url": self.url,
            "name": self.name,
            "active": self.active,
            "disabled": self.disabled,
            "extra_classes": self.extra_classes,
            "target_blank": self.target_blank,
            "led": self.led,
            "to_check": self.to_check,
            "ok_condition": self.ok_condition,
            "warning_condition": self.warning_condition,
            "error_condition": self.error_condition,
        }


class CustomSubMenuMixin:
    def add_sideframe_item_custom(
        self,
        name,
        url,
        active=False,
        disabled=False,
        extra_classes=None,
        on_close=None,
        side=LEFT,
        position=None,
        led=False,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        item = SideframeItemCustom(
            name,
            url,
            active=active,
            disabled=disabled,
            extra_classes=extra_classes,
            on_close=on_close,
            side=side,
            led=led,
            to_check=to_check,
            ok_condition=ok_condition,
            warning_condition=warning_condition,
            error_condition=error_condition,
        )
        self.add_item(item, position=position)
        return item

    def add_link_item_custom(
        self,
        name,
        url,
        active=False,
        disabled=False,
        extra_classes=None,
        side=LEFT,
        position=None,
        target_blank=False,
        led=False,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        item = LinkItemCustom(
            name,
            url,
            active=active,
            disabled=disabled,
            extra_classes=extra_classes,
            side=side,
            target_blank=target_blank,
            led=led,
            to_check=to_check,
            ok_condition=ok_condition,
            warning_condition=warning_condition,
            error_condition=error_condition,
        )
        self.add_item(item, position=position)
        return item


class CustomSubMenu(SubMenu, CustomSubMenuMixin):
    template = "toolbar/items/menu.html"
    sub_level = True
    active = False

    def __init__(
        self,
        name,
        csrf_token,
        disabled=False,
        side=LEFT,
        led=False,
        to_check=None,
        ok_condition=None,
        warning_condition=None,
        error_condition=None,
    ):
        ToolbarAPIMixin.__init__(self)
        BaseItem.__init__(self, side)
        self.name = name
        self.disabled = disabled
        self.csrf_token = csrf_token
        self.led = led
        self.to_check = to_check
        self.ok_condition = ok_condition
        self.warning_condition = warning_condition
        self.error_condition = error_condition

    def __repr__(self):
        return "<Menu:%s>" % force_str(self.name)

    def get_items(self):
        items = self.items
        for item in items:
            item.toolbar = self.toolbar
            if hasattr(item, "disabled"):
                item.disabled = self.disabled or item.disabled
        return items

    def get_context(self):
        return {
            "active": self.active,
            "disabled": self.disabled,
            "items": self.get_items(),
            "title": self.name,
            "sub_level": self.sub_level,
            "led": self.led,
            "to_check": self.to_check,
            "ok_condition": self.ok_condition,
            "warning_condition": self.warning_condition,
            "error_condition": self.error_condition,
        }
