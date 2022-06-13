from django.db import models


class UserInfo(models.Model):
    openId = models.CharField(max_length=30, primary_key=True)
    nickName = models.CharField(max_length=100, null=True)
    genderChoices = ((0, '未知'),
                     (1, '男'),
                     (2, '女'))
    gender = models.SmallIntegerField(choices=genderChoices, default=0)
    country = models.CharField(max_length=30, null=True)
    province = models.CharField(max_length=30, null=True)
    city = models.CharField(max_length=30, null=True)
    rewardPoints = models.IntegerField(default=0)
    stepNumbers = models.IntegerField(default=0)


class AddressInfo(models.Model):
    openId = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    genderChoices = ((1, '男'),
                     (2, '女'))
    gender = models.SmallIntegerField(choices=genderChoices)
    telephone = models.CharField(max_length=11)
    province = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    district = models.CharField(max_length=30)
    detail = models.CharField(max_length=100)
    isActive = models.BooleanField(default=False)

    class Meta:
        unique_together = (('openId', 'name', 'gender', 'telephone', 'province', 'city', 'district', 'detail'),)


class MedicineInfo(models.Model):
    openId = models.ForeignKey('UserInfo', on_delete=models.CASCADE)
    medicineName = models.CharField(max_length=50)
    instruction = models.CharField(max_length=30)
    times = models.CharField(max_length=30)
    remark = models.CharField(max_length=1000, null=True)

    class Meta:
        unique_together = (('openId', 'medicineName'),)
