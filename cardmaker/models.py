from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.

class Contact(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=13)
    email = models.CharField(max_length=100)
    content = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return 'Message from '+ self.name + "- " + self.email
    
class Usercomment(models.Model):
    sno = models.AutoField(primary_key=True)
    comment = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True)
    timeStamp = models.DateTimeField(default=now)

    def __str__(self):
        return self.comment[0:15] + "..." + " by " + self.user.username

class VisitingCard(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=1000)
    front_image = models.ImageField(upload_to="static/visitingcard",default="")
    back_image = models.ImageField(upload_to="static/visitingcard",default="")

class IdCard(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=500)
    image = models.ImageField(upload_to="static/idcard",default="")


class Resume(models.Model):
    id = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=500)
    image = models.ImageField(upload_to="static/resume",default="")