from django.conf.urls import url
#from user import views
from user.views import RegisterView,ActiveView,LoginView,LogoutView,UserInfoView,UserOrderView,UserAddrView


urlpatterns = [
    #url(r'^register$',views.register),
    #url(r'^register_handle$',views.register_handle),
	url(r'^register',RegisterView.as_view(),name='register'),
	url(r'active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
	url(r'^login',LoginView.as_view(),name='login'),
	url(r'^logout$',LogoutView.as_view(),name='logout'),
	url(r'^$',UserInfoView.as_view(),name='user'),
	url(r'^order$',UserOrderView.as_view(),name='order'),
	url(r'^addr$',UserAddrView.as_view(),name='address'),

]
