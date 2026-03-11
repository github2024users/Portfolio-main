from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from profiledetails.models import Projects, contactus

def homepage(request):
    insert_data = Projects.objects.all()
    data = {
        "insert_data": insert_data
    }
    return render(request, "index.html", data)

def Contactus(request):
    n = ""
    contact = contactus.objects.all()
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        en = contactus(name=name, email=email, phone=phone, desc=message)
        en.save()
        n = "message sent successfully"
        return redirect('/?success=true')
    return render(request, "index.html", {"n": n})

def register(request):
    return render(request, "register.html")

def login(request):
    return render(request, "login.html")

@login_required(login_url='login')
def dashboard(request):
    return render(request, "dashboard.html")