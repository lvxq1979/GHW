from django.db import models

# Create your models here.
class CarModel(models.Model):
    id = models.IntegerField(primary_key=True)
    carid = models.CharField(max_length=255, verbose_name="车源号")
    keywords = models.CharField(max_length=1024, verbose_name="关键字")
    description = models.CharField(max_length=1024, verbose_name="描述")
    url = models.CharField(max_length=1024, verbose_name="链接地址")

    def __unicode__(self):
        return self.carid

    class Meta:
        managed = False
        db_table = 'carlist'
        verbose_name = u"车辆信息"
        verbose_name_plural = verbose_name
