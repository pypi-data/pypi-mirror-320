
from wagtail_cookies_consent.models import CookieGroup, CookiesBanner          
from django import template

from wagtail_cookies_consent.util import (
    get_cookie_value_from_request,

)

register = template.Library()

@register.simple_tag
def CookiesGroup():
    cookie_group_list = CookieGroup.objects.all()

    return cookie_group_list

@register.simple_tag
def get_active_banner():
    return CookiesBanner.objects.order_by('-id').filter(active=True).first()


@register.filter
def cookie_group_accepted(request, arg):
    """
    Filter returns if cookie group is accepted.

    Examples:
    ::

        {{ request|cookie_group_accepted:"analytics" }}
        {{ request|cookie_group_accepted:"analytics=*:.google.com" }}
    """
    value = get_cookie_value_from_request(request, *arg.split("="))
    print(value)
    return value is True
@register.inclusion_tag('cookies_consent_wagtail/cookies_banner.html',takes_context=True,)
def cookies_banner(context,**style):
    print(style)
    active_banner=CookiesBanner.objects.order_by('-id').filter(active=True).first()
    return {"active_banner": active_banner,'style':style, "request": context.get("request")}


