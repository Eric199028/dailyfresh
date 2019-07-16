from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from user.models import User
from django.conf import settings
import re
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.mail import send_mail
from celery_tasks.tasks import send_active_email

# Create your views here.
#def index(request):
#	return HttpResponse("视图函数index")

def register(request):
	if request.method == 'GET':
		return render(request,'register.html')
	else:
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')
		# return render(request, 'register.html', {'errmsg': '数据不完整'})
		print('>' * 10)
		print(username, password, email, allow)

		if not all([username, password, email]):
			print('<' * 10)
			return render(request, 'register.html', {'errmsg': '数据不完整'})

		# if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5){1,2}$',email):
		#	return render(request,'register.html',{'errmsg':'邮箱地址不对'})

		if allow != 'on':
			# print('<' * 10)
			return render(request, 'register.html', {'errmsg': '请同意协议'})
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = None
		if user:
			return render(request, 'register.html', {'errmsg': '请同意协议'})

		user = User.objects.create_user(username, email, password)
		print('>' * 10)

		return redirect('/index.html')

class RegisterView(View):

	def get(self,request):
		return render(request,'register.html')

	def post(self,request):
		username = request.POST.get('user_name')
		password = request.POST.get('pwd')
		email = request.POST.get('email')
		allow = request.POST.get('allow')
		# return render(request, 'register.html', {'errmsg': '数据不完整'})

		#print(username, password, email, allow)

		if not all([username, password, email]):
			#print('<' * 10)
			return render(request, 'register.html', {'errmsg': '数据不完整'})

		if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
			return render(request,'register.html',{'errmsg':'邮箱地址不对'})

		if allow != 'on':
			# print('<' * 10)
			return render(request, 'register.html', {'errmsg': '请同意协议'})

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = None

		if user:
			return render(request, 'register.html', {'errmsg': '用户已存在'})

		user = User.objects.create_user(username, email, password)
		user.is_active = 0
		user.save()

		serializer = Serializer(settings.SECRET_KEY,3600)
		info = {'confirm':user.id}
		token = serializer.dumps(info) #dumps 注意s
		token = token.decode('utf8')

		send_active_email.delay(email,username,token)


		return redirect(reverse('goods:index'))


class ActiveView(View):
	def get(self,request,token):
		serializer = Serializer(settings.SECRET_KEY,3600)
		try :

			info = serializer.loads(token)
			user_id = info['confirm']
			user = User.objects.get(id=user_id)
			user.is_active = 1
			user.save()

			return redirect(reverse('user:login'))

		except SignatureExpired as e:
			return HttpResponse('激活链接已过期')


class LoginView(View):
	def get(self,request):
		return render(request,'login.html')


