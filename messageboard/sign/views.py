from random import randint

from django.contrib.auth import login, get_backends
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm, OneTimeCode, OneTimeCodeForm


def generate_otc():
    return str(randint(100000, 999999))


def register(request):
    if request.method == 'POST':
        form = BaseRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until it is confirmed
            user.username = user.email.split('@')[0]
            user.save()
            otc = generate_otc()
            OneTimeCode.objects.create(user=user, code=otc)

            send_mail(
                'Код для подтверждения регистрации',
                f'Ваш одноразовый код: {otc}',
                'Skillfactory MessageBoard <juliakarabasova@yandex.ru>',
                [user.email],
                fail_silently=False,
            )
            return redirect('validate_otc', user_id=user.id)
    else:
        form = BaseRegisterForm()

    return render(request, 'sign/signup.html', {'form': form})


def validate_otc(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = OneTimeCodeForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                otc = OneTimeCode.objects.get(user=user, code=code, is_used=False)
                user.is_active = True
                user.save()

                otc.is_used = True
                otc.save()

                backend = get_backends()[0]  # Assuming you are using the first backend in the list
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                login(request, user, backend=user.backend)

                return redirect('/')

            except OneTimeCode.DoesNotExist:
                form.add_error('code', 'Неверный код или код уже был использован')
    else:
        form = OneTimeCodeForm()
    return render(request, 'sign/validate_otc.html', {'form': form})
