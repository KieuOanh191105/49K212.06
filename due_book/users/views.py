# Views for Users App
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User

from .forms import UserRegisterForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/user_register.html'
    success_url = reverse_lazy('user_login')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                'Dang ky thanh cong! Chao mung {}.'.format(self.object.username)
            )
            return response
        except Exception as e:
            messages.error(self.request, 'Loi dang ky: {}'.format(str(e)))
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, str(error))
        return super().form_invalid(form)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Dang nhap thanh cong!')
            next_url = request.GET.get('next', reverse_lazy('home'))
            return redirect(next_url)
        else:
            messages.error(request, 'Ten dang nhap hoac mat khau khong dung!')
    else:
        form = AuthenticationForm()

    return render(request, 'users/user_login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'Ban da dang xuat!')
    return redirect('home')