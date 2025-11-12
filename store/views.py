from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Category, Writer, Book, Review, Slider
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import RegistrationForm, ReviewForm
from django.template.loader import render_to_string
from .forms import ForgotPasswordForm, ResetPasswordForm

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    newpublished = Book.objects.order_by('-created')[:15]
    slide = Slider.objects.order_by('-created')[:5]
    context = {
        "newbooks":newpublished,
        "slide": slide
    }
    return render(request, 'store/index.html', context)


def signin(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('store:index')
            else:
                messages.error(request, 'username and password doesn\'t match')

    return render(request, "store/login.html")	


def signout(request):
    logout(request)
    return redirect('store:index')	


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Welcome {user.username}!')
            return redirect('store:signin')
        else:
            # Error messages will be displayed through form.errors in template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'store/signup.html', {"form": form})


def payment(request):
    return render(request, 'store/payment.html')


def get_book(request, id):
    form = ReviewForm(request.POST or None)
    book = get_object_or_404(Book, id=id)
    rbooks = Book.objects.filter(category_id=book.category.id)
    r_review = Review.objects.filter(book_id=id).order_by('-created')

    paginator = Paginator(r_review, 4)
    page = request.GET.get('page')
    rreview = paginator.get_page(page)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if form.is_valid():
                temp = form.save(commit=False)
                temp.customer = User.objects.get(id=request.user.id)
                temp.book = book          
                temp = Book.objects.get(id=id)
                temp.totalreview += 1
                temp.totalrating += int(request.POST.get('review_star'))
                form.save()  
                temp.save()

                messages.success(request, "Review Added Successfully")
                form = ReviewForm()
        else:
            messages.error(request, "You need login first.")
    context = {
        "book":book,
        "rbooks": rbooks,
        "form": form,
        "rreview": rreview
    }
    return render(request, "store/book.html", context)


def get_books(request):
    books_ = Book.objects.all().order_by('-created')
    paginator = Paginator(books_, 10)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, "store/category.html", {"book":books})

def get_book_category(request, id):
    book_ = Book.objects.filter(category_id=id)
    paginator = Paginator(book_, 10)
    page = request.GET.get('page')
    book = paginator.get_page(page)
    return render(request, "store/category.html", {"book":book})

def get_writer(request, id):
    wrt = get_object_or_404(Writer, id=id)
    book = Book.objects.filter(writer_id=wrt.id)
    context = {
        "wrt": wrt,
        "book": book
    }
    return render(request, "store/writer.html", context)


def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset link
            reset_link = request.build_absolute_uri(
                f'/reset-password/{uid}/{token}/'
            )
            
            messages.success(
                request, 
                f'Password reset link generated! Click here to reset: {reset_link}'
            )
            return redirect('store:forgot-password')
            
            # UNCOMMENT THIS FOR PRODUCTION (when email is configured)
            # # Send email
            # subject = 'Reset Your BookStore Password'
            # message = render_to_string('store/password_reset_email.html', {
            #     'user': user,
            #     'reset_link': reset_link,
            # })
            # 
            # send_mail(
            #     subject,
            #     message,
            #     settings.EMAIL_HOST_USER,
            #     [email],
            #     fail_silently=False,
            # )
            # 
            # messages.success(request, 'Password reset link has been sent to your email!')
            # return redirect('store:signin')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'store/forgot-password.html', {'form': form})

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully! You can now login.')
                return redirect('store:signin')
        else:
            form = ResetPasswordForm(user)
        
        return render(request, 'store/reset-password.html', {'form': form})
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('store:forgot-password')

