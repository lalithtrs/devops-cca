from django.conf.urls import handler404
from django.urls import path
from . import views

handler404 = 'bankapp.views.pagenotfound'

urlpatterns = [
    path('', views.homepage, name='bhomepage'),
    path('home-page', views.homepage, name='bhomepage'),
    path('about-us', views.aboutus, name='baboutus'),
    path('contact-us', views.contactus, name='bcontactus'),
    path('list-account', views.listaccount, name='blistaccount'),
    path('add-account', views.addaccount, name='baddaccount'),
    path('update-account/<int:id>', views.updateaccount, name='bupdateaccount'),
    path('delete-account/<int:id>', views.deleteaccount, name='bdeleteaccount'),
    path('page-not-found', views.pagenotfound, name='bpagenotfound'),
    path('user-login', views.userlogin, name='buserlogin'),
    path('user-register', views.userregister, name='buserregister'),
    path('user-logout', views.userlogout, name='buserlogout'),
    path('user-transaction', views.usertransaction, name='busertransaction'),
    path('user-feedback', views.userfeedback, name='buserfeedback'),
]