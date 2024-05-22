from django.contrib import admin
from cardmaker.models import Contact,Usercomment,VisitingCard,IdCard,Resume

# Register your models here.
admin.site.register(Contact)
admin.site.register(Usercomment)
admin.site.register(VisitingCard)
admin.site.register(IdCard)
admin.site.register(Resume)