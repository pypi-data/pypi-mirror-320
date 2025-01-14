from django.shortcuts import render
from wagtail_cookies_consent.models import CookieGroup,Cookie,CookiesBanner
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup
from django.views import View
import json
from datetime import datetime,timezone
from django.http import JsonResponse
class CookieGroupsViewSet(SnippetViewSet):
    model = CookieGroup
    icon = "cogs"
    menu_label = "CookieGroups"
    menu_name = "CookieGroups"

class CookiesViewSet(SnippetViewSet):
    model = Cookie
    icon = "cogs"
    menu_label = "Cookies"
    menu_name = "Cookies"

class CookiesBannerViewSet(SnippetViewSet):
    model = CookiesBanner
    icon = "cogs"
    menu_label = "CookiesBanner"
    menu_name = "CookiesBanner"
    list_display  = ['name','active']


class CookiesViewSetGroup(SnippetViewSetGroup):
    items = (CookiesBannerViewSet, CookiesViewSet,CookieGroupsViewSet)
    menu_icon = "cog"
    menu_label = "Cookies consent"
    menu_name = "Cookies consent"



class CookiesViews(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "invalid Json"}, status=400)
        cookie_group_list = CookieGroup.objects.all()
        formatted_time = datetime.now(timezone.utc).isoformat()

        if data.get("request") == "allow":
            cookie_consent_list = [f"{item.varname}={formatted_time}" for item in cookie_group_list]
        elif data.get("request") == "customize":
            cookie_consent_list = [f"{item}={formatted_time}" for item in data.get("accepted")]
            for item in cookie_group_list:
                if item.is_required is True:
                    cookie_consent_list.append(f"{item.varname}={formatted_time}")
        else:
            cookie_consent_list = [f"{item.varname}={formatted_time}" if item.varname == "required" else f"{item.varname} =-1" for item in cookie_group_list]

        response = JsonResponse({"error": "invalid Json"}, status=200)
        all_cookie_consent = "|".join(cookie_consent_list)
        response.set_cookie(
            key="cookie_consent",
            value=all_cookie_consent,
            max_age=31536000000,
            samesite="Lax",
        )
        return response