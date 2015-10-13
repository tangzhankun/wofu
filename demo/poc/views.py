from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from novaclient import client
import logging
import time

logger = logging.getLogger(__name__)
# Create your views here.
def register(request):
    user_name = request.POST.get('name')
    user_pwd = request.POST.get('passwd')
    already_have = User.objects.filter(username=user_name).exists()
    if already_have:
        return JsonResponse({"tip":'no'})
    #save to db
    u = User.objects.create_user(user_name,None,user_pwd);
    #set namespace
    namespace = u.id
    #use nova to start an vm
    vm_id = startVM(namespace)
    if vm_id == False:
        return JsonResponse({"tip":'vm_failed'})
    u.first_name = vm_id
    u.save()
    #return ip of VM
    url = getIP(vm_id) + ":9000"
    user = authenticate(username=user_name, password=user_pwd)
    _login(request,user)
    return JsonResponse({"tip":'ok',"cdap_url":'%s'%url})

def startVM(namespace):
    nova = client.Client("2","tangzhankun","123456","tangzhankun", "http://172.16.6.11:35357/v2.0")
    i = nova.images.find(name="CentOS-6.6")
    f = nova.flavors.find(name="m1.medium")
    cmd = "echo 'hello_world' > /root/op.txt\n"
    ci = "#cloud-config\nruncmd:\n - " + cmd
    instance = nova.servers.create(name='%s'%namespace,image=i.id,flavor=f.id,userdata=ci,key_name="temp_key")
    server_id = instance.id
    if waitUntil(checkVM,120,1,nova,server_id):
        return server_id
    return False

def checkVM(nova,serverid):
    instance = nova.servers.get(serverid)
    return instance.status == "ACTIVE"

def waitUntil(condition_function, timeout, period=1, *args, **kwargs):
    mustend = time.time() + timeout
    while time.time() < mustend:
        if condition_function(*args,**kwargs):
            return True
        time.sleep(period)
    return False

def getIP(vm_id):
    nova = client.Client("2","tangzhankun","123456","tangzhankun", "http://172.16.6.11:35357/v2.0")
    ips = nova.servers.ips(vm_id)
    return ips["demo-net"][0]["addr"]
 
def index(request):
    if request.user.is_authenticated():
        vm_id = request.user.first_name
        cdap_url = getIP(vm_id) + ":9000"
        return render(request,'poc/home.html',{'name':request.user.username,'cdap_url':cdap_url})
    return render(request,'poc/home.html',{'login_already':'false'})

def login(request):
    user_name = request.POST.get('name')
    user_pwd = request.POST.get('passwd')
    #check user
    user = authenticate(username=user_name, password=user_pwd)
    if user is not None:
        if user.is_active:
            _login(request,user)
            vm_id = user.first_name
            #get VM's IP
            cdap_url = getIP(vm_id) + ":9000"
            return JsonResponse({"name":'%s'%user_name,"login_already":'true',"cdap_url":cdap_url})
    else:
        return JsonResponse({"name":'',"login_already":'false'})
    
def logout(request):
    #destroy session
    _logout(request)
    return JsonResponse({"tip":'ok'})
