from django.shortcuts import render, redirect

def login_view(request):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == 'admin@gmail.com' and password == '123':
            return redirect('dashboard')  # redirect to success page
        else:
            error = "Invalid credentials. Try again."

    return render(request, './login/login.html', {'error': error})

def dashboard_view(request):
    return render(request, './Dashboard/dashboard.html')
