from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, User, Order, OrderItem
from .forms import UserRegistrationForm, LoginForm, OrderCreateForm
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def index(request):
    #Эта функция отображает главную страницу
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products':products})


@login_required
def account(request):
    # Эта функция отображает
    user = User.objects.get(id=request.user.id)
    return render(request,'shop/account.html', {'users':user})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Создает нового пользователя, но без сохранения
            new_user = form.save(commit=False)
            # Установить пароль
            new_user.set_password(form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'shop/account.html', {'new_user': new_user})
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            cd = form.cleaned_data
            user = User.objects.get(email=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Авторизация прошла успешно')
                else:
                    return HttpResponse('Аккаунт отключен')
            else:
                return HttpResponse('Введен неправильный логин/пароль')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id)
        # Получение текущей корзины из сессии
        cart = request.session.get('cart', {})
        if product_id in cart:
            cart[product_id] += quantity  # Увеличиваем количество, если товар уже в корзине
        else:
            cart[product_id] = quantity # Добавляем товар в корзину
        request.session['cart'] = cart  # Сохраняем обновленную корзину в сессии
        return redirect('cart')  # Перенаправляем пользователя на страницу корзины
    return HttpResponse("Only POST method is allowed", status=405)


@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart',{})
        quantity = int(request.POST.get('quantity', 1))
        if product_id in cart:
            del cart[product_id]
        request.session['cart'] = cart
        return redirect('cart')


@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0
    if request.method == 'POST':
        # Обновление корзины
        index = 1
        while f'product_id_{index}' in request.POST:
            product_id = request.POST[f'product_id_{index}']
            new_quantity = int(request.POST.get(f'quantity_{index}', 0))
            if new_quantity <= 0:
                remove_from_cart(request, product_id=product_id)
            else:
                cart[product_id] = new_quantity  # Обновляем количество
            index += 1

        request.session['cart'] = cart  # Сохраняем обновленную корзину в сессии
        return redirect('cart')  # Перенаправляем пользователя на страницу корзины

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total_price += product.price * quantity
        products.append({'product': product, 'quantity': quantity})

    return render(request, 'shop/cart.html', {'products': products, 'total_price': total_price})


def user_logout(request):
    logout(request)  # Функция logout завершает сеанс для текущего пользователя
    return redirect('logout')


@login_required
def create_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart')
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            order.save()
            for key, value in cart.items():
                try:
                    product = Product.objects.get(pk=key)
                    price = product.price * value
                    order_item = OrderItem(order=order, product=product, quantity=value, price=price)
                    order_item.save()
                except Product.DoesNotExist:
                    messages.error(request, f'Продукт с ID {key} не найден.')
                    return redirect('cart')  # Или другая подходящая страница
            messages.success(request, 'Ваш заказ был оформлен!')
            cart.clear()
            return render(request, 'shop/order_success.html', {'order': order})
    else:
        form = OrderCreateForm()
    return render(request, 'shop/order_create.html', {'form': form})


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})