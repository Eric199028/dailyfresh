from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from user.models import User,Address
from utils.mixin import LoginRequiredMixin
from django.contrib.auth import authenticate, login,logout
from django.conf import settings
import re
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.mail import send_mail
from celery_tasks.tasks import send_active_email
from django_redis import get_redis_connection

# Create your views here.


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
		if 'username' in request.COOKIES:
			username = request.COOKIES.get('username')
			checked = 'checked'
		else:
			username = ''
			checked = ''
		return render(request,'login.html',{'username':username,'checked':checked})

	def post(self,request):
		username = request.POST.get('username')
		password = request.POST.get('pwd')
		user = authenticate(username=username,password=password)

		if user is not None:
			# 用户名密码正确
			if user.is_active:
				response  = redirect(reverse('goods:index'))
				login(request,user)
				remember = request.POST.get('remember')
				if remember == 'on':
					response.set_cookie('username',username,max_age=7*24*3600)
				else:
					response.delete_cookie('username')
				return response
			else:
				return render(request,'login.html',{'errmsg':'用户未激活'})
		else:
			return render(request,'login.html',{'errmsg':'用户密码错误'})

class LogoutView(View):
	def get(self,request):
		logout(request)
		return redirect(reverse('good:index'))


class UserInfoView(LoginRequiredMixin,View):
	def get(self, request):

		user = request.user
		address = Address.objects.get_default_address(user)
		con = get_redis_connection('default')

		history_key = 'history_%d' % user.id
		# 获取用户最新浏览的5个商品的id
		sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]

		# 从数据库中查询用户浏览的商品的具体信息
		# goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
		#
		# goods_res = []
		# for a_id in sku_ids:
		#     for goods in goods_li:
		#         if a_id == goods.id:
		#             goods_res.append(goods)

		# 遍历获取用户浏览的商品信息
		goods_li = []
		for id in sku_ids:
			goods = GoodsSKU.objects.get(id=id)
			goods_li.append(goods)


		# 获取用户的历史浏览记录
		# from redis import StrictRedis
		# sr = StrictRedis(host='172.16.179.130', port='6379', db=9)


		# for id in sku_ids:
		# 	goods = GoodsSKU.objects.get(id=id)
		# 	goods_li.append(goods)

		# 组织上下文
		context = {'page': 'user',
		           'address': address,
		           'goods_li': goods_li}

		return render(request,'user_center_info.html',context)

class UserOrderView(LoginRequiredMixin,View):
	def get(self,request):
		return render(request,'user_center_order.html',{'page':'order'})

class UserAddrView(LoginRequiredMixin,View):
	def get(self,request):
		user = request.user
		address = Address.objects.get_default_address(user)


		# 使用模板
		return render(request, 'user_center_site.html', {'page': 'address', 'address': address})


	def post(self,request):

		receiver = request.POST.get('receiver')
		addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		phone = request.POST.get('phone')

		# if not all ([receive,addr,phone]):
		# 	return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})
		user = request.user
		address = Address.objects.get_default_address(user)
		print('*'*10)

		if address:
			is_default = False
			print(is_default)
		else:
			is_default = True
			print(is_default)

		# 添加地址
		Address.objects.create(user=user,
		                       receiver=receiver,
		                       addr=addr,
		                       zip_code=zip_code,
		                       phone=phone,
		                       is_default=is_default)

		# 返回应答,刷新地址页面
		return redirect(reverse('user:address'))  # get请求方式


