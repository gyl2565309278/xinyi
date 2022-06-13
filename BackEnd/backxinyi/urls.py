"""backxinyi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp.views import *

urlpatterns = [
    path('data/year/', HeartRate.getYearData),
    path('data/month/', HeartRate.getMonthData),
    path('data/week/', HeartRate.getWeekData),
    path('medicine/deleteMedicine/', Medicine.deleteMedicine),
    path('medicine/updateMedicine/', Medicine.updateMedicine),
    path('medicine/addMedicine/', Medicine.addMedicine),
    path('medicine/', Medicine.getMedicine),
    path('address/deleteAddress/', Address.deleteAddress),
    path('address/updateAddress/', Address.updateAddress),
    path('address/addAddress/', Address.addAddress),
    path('address/changeActivate/', Address.changeActivate),
    path('address/', Address.getAddress),
    path('userInfo/', UserInfo.getUserInfo),
    path('userQuery/', UserInfo.getUserQuery),
    path('decrypt/', Decrypt.getOpenId),
    path('admin/', admin.site.urls),
    path('helloWorld/', Hello),
]
