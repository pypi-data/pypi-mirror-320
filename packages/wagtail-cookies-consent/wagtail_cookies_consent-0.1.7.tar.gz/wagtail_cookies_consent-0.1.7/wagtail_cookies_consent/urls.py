from django.urls import path ,include

from wagtail_cookies_consent.views import CookiesViews
urlpatterns=[
    path('accept_cookies/',CookiesViews.as_view(),name='accept_cookies')
]