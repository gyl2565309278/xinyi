import json
import os
import re
import requests
from django.shortcuts import HttpResponse
from mainapp import models
from urllib import request
from backxinyi.settings import STATICFILES_DIRS


def Hello(request):
    return HttpResponse('Hello World!')


class Decrypt:
    @staticmethod
    def _code2Session(appId: str, appSecret: str, jsCode: str) -> dict:
        loginUrl = 'https://api.weixin.qq.com/sns/jscode2session'
        loginParam = {
            'appid': appId,
            'secret': appSecret,
            'js_code': jsCode,
            'grant_type': 'authorization_code'
        }
        res = requests.get(url=loginUrl, params=loginParam)
        return res.json()

    @staticmethod
    def getOpenId(request):
        resInfo = Decrypt._code2Session(
            request.POST['appId'],
            request.POST['appSecret'],
            request.POST['code'])
        return HttpResponse(json.dumps(resInfo))


class UserInfo:
    @staticmethod
    def _downloadImage(url, openId):
        req = request.Request(url)
        res = request.urlopen(req)
        getImage = res.read()
        with open(os.path.join(STATICFILES_DIRS[0], '{}.jpg'.format(openId)), 'wb')as f:
            f.write(getImage)

    @staticmethod
    def getUserQuery(request):
        hasUser = models.UserInfo.objects.filter(openId=request.POST['openId']).count()
        assert hasUser <= 1
        if hasUser == 0:
            res = {'openId': request.POST['openId']}
            return HttpResponse(json.dumps(res))
        else:
            userInfo = models.UserInfo.objects.get(openId=request.POST['openId'])
            res = {
                'openId': userInfo.openId,
                'nickName': userInfo.nickName,
                'gender': userInfo.gender,
                'avatarUrl': 'static/{}.jpg'.format(request.POST['openId']),
                'country': userInfo.country,
                'province': userInfo.province,
                'city': userInfo.city,
                'rewardPoints': userInfo.rewardPoints,
                'stepNumbers': userInfo.stepNumbers,
            }
            return HttpResponse(json.dumps(res))

    @staticmethod
    def getUserInfo(request):
        if models.UserInfo.objects.filter(openId=request.POST['openId']).count() == 0:
            UserInfo._downloadImage(request.POST['avatarUrl'], request.POST['openId'])
            models.UserInfo.objects.create(
                openId=request.POST['openId'],
                nickName=request.POST['nickName'],
                gender=request.POST['gender'],
                country=request.POST['country'],
                province=request.POST['province'],
                city=request.POST['city'],
            )
        userInfo = models.UserInfo.objects.get(openId=request.POST['openId'])
        res = {
            'nickName': userInfo.nickName,
            'gender': userInfo.gender,
            'avatarUrl': 'static/{}.jpg'.format(request.POST['openId']),
            'country': userInfo.country,
            'province': userInfo.province,
            'city': userInfo.city,
            'rewardPoints': userInfo.rewardPoints,
            'stepNumbers': userInfo.stepNumbers,
        }
        return HttpResponse(json.dumps(res))


class Address:
    @staticmethod
    def _getAddresses(openId):
        res = []
        addresses = models.AddressInfo.objects.filter(openId=openId).order_by('pk')
        for address in addresses:
            res.append({
                'id': address.pk,
                'name': address.name,
                'gender': address.gender,
                'telephone': address.telephone,
                'province': address.province,
                'city': address.city,
                'district': address.district,
                'detail': address.detail,
                'isActive': address.isActive,
            })
        return HttpResponse(json.dumps(res))

    @staticmethod
    def getAddress(request):
        return Address._getAddresses(request.POST['openId'])

    @staticmethod
    def changeActivate(request):
        deactivate = models.AddressInfo.objects.filter(openId=request.POST['openId']).get(isActive=True)
        deactivate.isActive = False
        deactivate.save()
        activate = models.AddressInfo.objects.filter(openId=request.POST['openId']).get(pk=request.POST['activateId'])
        activate.isActive = True
        activate.save()
        return Address._getAddresses(request.POST['openId'])

    @staticmethod
    def addAddress(request):
        try:
            addressCount = models.AddressInfo.objects.filter(openId=request.POST['openId']).count()
            if addressCount == 0:
                models.AddressInfo.objects.create(
                    pk=addressCount,
                    openId=models.UserInfo.objects.get(openId=request.POST['openId']),
                    name=request.POST['name'],
                    gender=request.POST['gender'],
                    telephone=request.POST['telephone'],
                    province=request.POST['province'],
                    city=request.POST['city'],
                    district=request.POST['district'],
                    detail=request.POST['detail'],
                    isActive=True,
                )
            else:
                models.AddressInfo.objects.create(
                    pk=addressCount,
                    openId=models.UserInfo.objects.get(openId=request.POST['openId']),
                    name=request.POST['name'],
                    gender=request.POST['gender'],
                    telephone=request.POST['telephone'],
                    province=request.POST['province'],
                    city=request.POST['city'],
                    district=request.POST['district'],
                    detail=request.POST['detail'],
                    isActive=False,
                )
        finally:
            return Address._getAddresses(request.POST['openId'])

    @staticmethod
    def updateAddress(request):
        updateInfo = models.AddressInfo.objects.get(openId=request.POST['openId'], pk=request.POST['id'])
        updateInfo.name = request.POST['name']
        updateInfo.gender = request.POST['gender']
        updateInfo.telephone = request.POST['telephone']
        updateInfo.province = request.POST['province']
        updateInfo.city = request.POST['city']
        updateInfo.district = request.POST['district']
        updateInfo.detail = request.POST['detail']
        updateInfo.save()
        return Address._getAddresses(request.POST['openId'])

    @staticmethod
    def deleteAddress(request):
        deleteInfo = models.AddressInfo.objects.get(openId=request.POST['openId'], pk=request.POST['id'])
        isActiveInfo = deleteInfo.isActive
        deleteInfo.delete()
        addresses = models.AddressInfo.objects.filter(openId=request.POST['openId']).order_by('pk')
        for address in addresses:
            if address.pk > int(request.POST['id']):
                pk = address.pk - 1
                name = address.name
                gender = address.gender
                telephone = address.telephone
                province = address.province
                city = address.city
                district = address.district
                detail = address.detail
                isActive = address.isActive
                address.delete()
                models.AddressInfo.objects.create(
                    pk=pk,
                    openId=models.UserInfo.objects.get(openId=request.POST['openId']),
                    name=name,
                    gender=gender,
                    telephone=telephone,
                    province=province,
                    city=city,
                    district=district,
                    detail=detail,
                    isActive=isActive,
                )
        if isActiveInfo and addresses.count() != 0:
            tmpAddress = addresses.get(pk=0)
            tmpAddress.isActive = True
            tmpAddress.save()
        return Address._getAddresses(request.POST['openId'])


class Medicine:
    @staticmethod
    def _getMedicines(openId):
        res = []
        medicines = models.MedicineInfo.objects.filter(openId=openId).order_by('pk')
        for medicine in medicines:
            res.append({
                'id': medicine.pk,
                'medicineName': medicine.medicineName,
                'instruction': medicine.instruction,
                'times': medicine.times,
                'remark': medicine.remark,
            })
        return HttpResponse(json.dumps(res))

    @staticmethod
    def getMedicine(request):
        return Medicine._getMedicines(request.POST['openId'])

    @staticmethod
    def addMedicine(request):
        try:
            medicineCount = models.MedicineInfo.objects.filter(openId=request.POST['openId']).count()
            models.MedicineInfo.objects.create(
                pk=medicineCount,
                openId=models.UserInfo.objects.get(openId=request.POST['openId']),
                medicineName=request.POST['medicineName'],
                instruction=request.POST['instruction'],
                times=request.POST['times'],
                remark=request.POST['remark'],
            )
        finally:
            return Medicine._getMedicines(request.POST["openId"])

    @staticmethod
    def updateMedicine(request):
        updateInfo = models.MedicineInfo.objects.get(openId=request.POST["openId"], pk=request.POST["id"])
        updateInfo.medicineName = request.POST["medicineName"]
        updateInfo.instruction = request.POST["instruction"]
        updateInfo.times = request.POST["times"]
        updateInfo.remark = request.POST["remark"]
        updateInfo.save()
        return Medicine._getMedicines(request.POST["openId"])

    @staticmethod
    def deleteMedicine(request):
        deleteInfo = models.MedicineInfo.objects.get(openId=request.POST["openId"], pk=request.POST["id"])
        deleteInfo.delete()
        medicines = models.MedicineInfo.objects.filter(openId=request.POST["openId"]).order_by("pk")
        for medicine in medicines:
            if medicine.pk > int(request.POST["id"]):
                pk = medicine.pk - 1
                medicineName = medicine.medicineName
                instruction = medicine.instruction
                times = medicine.times
                remark = medicine.remark
                medicine.delete()
                models.MedicineInfo.objects.create(
                    pk=pk,
                    openId=models.UserInfo.objects.get(openId=request.POST["openId"]),
                    medicineName=medicineName,
                    instruction=instruction,
                    times=times,
                    remark=remark,
                )
        return Medicine._getMedicines(request.POST["openId"])


class HeartRate:
    @staticmethod
    def _getMonthNumber(year_month):
        year, month = year_month.split('-')
        year, month = int(year), int(month)
        days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if year % 4 == 0:
            if year % 100 != 0:
                days[1] = 29
            else:
                if year % 400 == 0:
                    days[1] = 29
        return days[month - 1]

    @staticmethod
    def getWeekData(request):
        weekPattern = re.compile(r"(.*)年(.*)月(.*)日 - (.*)年(.*)月(.*)日")
        weekMatch = weekPattern.match(request.POST["weekRangeString"])
        startYear = weekMatch.group(1)
        startMonth = weekMatch.group(2)
        startDay = int(weekMatch.group(3))
        endYear = weekMatch.group(4)
        endMonth = weekMatch.group(5)
        endDay = int(weekMatch.group(6))

        weeks = []
        if endDay >= 7:
            for day in range(startDay, endDay + 1):
                weeks.append(endYear + "-" + endMonth + "-" + "%02d" % day)
        else:
            last = 7 - endDay
            for day in range(startDay, startDay + last):
                weeks.append(startYear + "-" + startMonth + "-" + "%02d" % day)
            for day in range(1, endDay + 1):
                weeks.append(endYear + "-" + endMonth + "-" + "%02d" % day)

        res = []
        for week in weeks:
            try:
                with open("data/heartRate/{}_{}.txt".format(request.POST["openId"], week), 'r') as f:
                    heartRateList = f.readlines()
                    if len(heartRateList) == 1441:
                        minHeartRate, maxHeartRate = heartRateList[1440].split(' ')
                        res.append({
                            "date": week,
                            "hasData": True,
                            "minHeartRate": int(minHeartRate),
                            "maxHeartRate": int(maxHeartRate)
                        })
                    else:
                        res.append({
                            "date": week,
                            "hasData": False
                        })
            except FileNotFoundError:
                res.append({
                    "date": week,
                    "hasData": False
                })
        return HttpResponse(json.dumps(res))

    @staticmethod
    def getMonthData(request):
        hasMonthData = False
        days = HeartRate._getMonthNumber(request.POST["month"])
        monthData = []
        for day in range(1, days + 1):
            date = request.POST["month"] + "-" + "%02d" % day
            try:
                with open("data/heartRate/" + request.POST["openId"] + "_" + date + ".txt", 'r') as f:
                    heartRateList = f.readlines()
                    if len(heartRateList) == 1441:
                        minHeartRate, maxHeartRate = heartRateList[1440].split(' ')
                        monthData.append({
                            "date": date,
                            "hasData": True,
                            "minHeartRate": int(minHeartRate),
                            "maxHeartRate": int(maxHeartRate)
                        })
                        hasMonthData = True
                    else:
                        monthData.append({
                            "date": date,
                            "hasData": False
                        })
            except FileNotFoundError:
                monthData.append({
                    "date": date,
                    "hasData": False
                })
        return HttpResponse(json.dumps({
            "hasMonthData": hasMonthData,
            "monthData": monthData
        }))

    @staticmethod
    def getYearData(request):
        hasYearData = False
        yearData = []
        currentYear, currentMonth, currentDay = request.POST["currentDate"].split('-')
        if request.POST["year"] == currentYear:
            current_month = int(currentMonth)
            for month in range(1, current_month):
                try:
                    with open("data/heartRate/{}_{}-{}.txt".format(request.POST["openId"], request.POST["year"],
                                                                   "%02d" % month), 'r') as f:
                        heartRateList = f.readlines()
                        minHeartRate, maxHeartRate = heartRateList[0].split(' ')
                        yearData.append({
                            "month": str(month),
                            "hasData": True,
                            "minHeartRate": int(minHeartRate),
                            "maxHeartRate": int(maxHeartRate)
                        })
                except FileNotFoundError:
                    yearData.append({
                        "month": str(month),
                        "hasData": False
                    })
            current_day = int(currentDay)
            minHeartRate = 1000
            maxHeartRate = 0
            for day in range(1, current_day + 1):
                try:
                    with open("data/heartRate/{}_{}-{}-{}.txt".format(request.POST["openId"],
                                                                      currentYear, currentMonth, day), 'r') as f:
                        heartRateList = f.readlines()
                        if len(heartRateList) == 1441:
                            minDayHeartRate, maxDayHeartRate = heartRateList[1440].split(' ')
                            minHeartRate = min(minHeartRate, int(minDayHeartRate))
                            maxHeartRate = max(maxHeartRate, int(maxDayHeartRate))
                        else:
                            for heartRate in heartRateList:
                                minHeartRate = min(minHeartRate, int(heartRate))
                                maxHeartRate = max(maxHeartRate, int(heartRate))
                except FileNotFoundError:
                    pass
            yearData.append({
                "month": str(current_month),
                "hasData": True,
                "minHeartRate": int(minHeartRate),
                "maxHeartRate": int(maxHeartRate)
            })
            hasYearData = True
            for month in range(current_month + 1, 13):
                yearData.append({
                    "month": str(month),
                    "hasData": False
                })
        else:
            for month in range(1, 13):
                try:
                    with open("data/heartRate/{}_{}-{}.txt".format(request.POST["openId"],
                                                                   request.POST["year"], "%02d" % month), 'r') as f:
                        heartRateList = f.readlines()
                        minHeartRate, maxHeartRate = heartRateList[0].split(' ')
                        yearData.append({
                            "month": str(month),
                            "hasData": True,
                            "minHeartRate": int(minHeartRate),
                            "maxHeartRate": int(maxHeartRate)
                        })
                        hasYearData = True
                except FileNotFoundError:
                    yearData.append({
                        "month": str(month),
                        "hasData": False
                    })
        return HttpResponse(json.dumps({
            "hasYearData": hasYearData,
            "yearData": yearData
        }))
