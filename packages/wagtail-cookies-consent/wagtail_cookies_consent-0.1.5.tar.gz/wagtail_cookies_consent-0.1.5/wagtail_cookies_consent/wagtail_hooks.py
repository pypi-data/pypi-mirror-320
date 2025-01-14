from wagtail import hooks
from wagtail_cookies_consent.views import CookiesViewSetGroup

@hooks.register('register_admin_viewset')
def register_viewset():
    return CookiesViewSetGroup()
