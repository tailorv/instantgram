from django.shortcuts import render, redirect, get_object_or_404
from .models import Image,Profile,Follow
from .forms import UploadForm,ProfileForm,UpdateUserForm,UpdateUserProfileForm,CommentForm,UserSignUpForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .email import send_welcome_email
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes,force_text,DjangoUnicodeDecodeError
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls.base import reverse
from  django.http import HttpResponse
from django.contrib.auth import authenticate,login, logout




def usersignup(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            link=reverse('activate',kwargs={'uidb64':uidb64,'token':account_activation_token.make_token(user)})
            activate_url='http://'+domain+link
            
            email_body='Hi ' +user.username+ ' Please use this link to verify your account\n' +activate_url
            
            email_subject = 'Activate Your Account'
            
            to_email = form.cleaned_data.get('email')
            
            email = EmailMessage(email_subject, email_body, 'francis.kinyae@student.moringaschool.com',[to_email])
            
            email.send()
            
            return render(request, "email/invitation.html")

    else:
        
        form = UserSignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, "email/welcomeemail.html")
        
    else:
        return render(request, "email/invalid.html")
    
    
    

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
    images = Image.images()
    users = User.objects.exclude(id=request.user.id)
    return render(request,"index.html", {"images":images[::1],"users":users})

def post(request):
    if request.method == 'POST':        
        form = UploadForm(request.POST,request.FILES)
        print(form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.profile
            post.save()
            return redirect('index')
    else:
        form = UploadForm()
    return render(request, 'post_image.html', {"form":form})

@login_required(login_url='/accounts/login/')
def profile(request, username):
    images = request.user.profile.images.all()
    print(images)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        prof_form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and prof_form.is_valid():
            user_form.save()
            prof_form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        user_form = UpdateUserForm(instance=request.user)
        prof_form = UpdateUserProfileForm(instance=request.user.profile)
    params = {
        'user_form': user_form,
        'prof_form': prof_form,
        
    }
    return render(request, 'profile.html', params)

@login_required(login_url='/accounts/login/')
def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES)
        print(form.errors)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('profile')
    else:
        form = UploadForm()
    return render(request,'edit_profile.html',{"form":form})

@login_required(login_url='/accounts/login/')
def search_profile(request):
    if 'search_user' in request.GET and request.GET['search_user']:
        name = request.GET.get("search_user")
        results = Profile.search_profile(name)
        print(results)
        message = f'name'
        params = {
            'results': results,
            'message': message
        }
        return render(request, 'results.html', params)
    else:
        message = "You did not make a selection"
    return render(request, 'results.html', {'message': message})

@login_required(login_url='/accounts/login/')
def user_profile(request, username):
    user_prof = get_object_or_404(User, username=username)
    if request.user == user_prof:
        return redirect('profile', username=request.user.username)
    user_posts = user_prof.profile.images.all()
    
    followers = Follow.objects.filter(followed=user_prof.profile)
    follow_status = None
    for follower in followers:
        if request.user.profile == follower.follower:
            follow_status = True
        else:
            follow_status = False
    params = {
        'user_prof': user_prof,
        'user_posts': user_posts,
        'followers': followers,
        'follow_status': follow_status
    }
    return render(request, 'user_profile.html', params)

login_required(login_url='/accounts/login/')
def follow(request, to_follow):
    if request.method == 'GET':
        user_three_profile = Profile.objects.get(pk=to_follow)
        follow_s = Follow(follower=request.user.profile, followed=user_three_profile)
        follow_s.save()
        return redirect('user_profile', user_three_profile.user.username)

@login_required(login_url='/accounts/login/')
def unfollow(request, to_unfollow):
    if request.method == 'GET':
        user_two_profile = Profile.objects.get(pk=to_unfollow)
        unfollow_d = Follow.objects.filter(follower=request.user.profile, followed=user_two_profile)
        unfollow_d.delete()
        return redirect('user_profile', user_two_profile.user.username)


@login_required(login_url='/accounts/login/')
def comment(request, id):
    image = get_object_or_404(Image, pk=id)
    comments = image.comment.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.photo = image
            comment.user = request.user.profile
            comment.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = CommentForm()
    params = {
        'image': image,
        'form': form,
        'comments':comments,
    }
    return render(request, 'post.html', params)
