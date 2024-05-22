from django.urls import path
from cardmaker import views

urlpatterns = [
    path('',views.home,name='home'),
    path('contact',views.contact,name='contact'),
    path('about',views.about,name='about'),
    path('comment',views.comment,name='comment'),
    path('signup',views.handleSignup,name='handleSignup'),
    path('login',views.handleLogin,name='handleLogin'),
    path('logout',views.handleLogout,name='handleLogout'),
    path('viewComment',views.viewComment,name="viewComment"),
    path('postComment',views.postComment,name="postComment"),
    path('visitingcard',views.visitingcard,name="visitingcard"),
    path('generate_visiting_card',views.generate_visiting_card,name="generate_visiting_card"),
    path('idcard',views.idcard,name="idcard"),
    path('generate_id_card',views.generate_id_card,name="generate_id_card"),
    path('resume',views.resume,name="resume"),
    path('generate_resume_card',views.generate_resume_card,name="generate_resume_card"),
]