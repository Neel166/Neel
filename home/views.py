from django.shortcuts import render, HttpResponse, redirect
from home.models import Contact
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from blog.models import Post
import requests
import json

def home(request):
    return render(request, 'home/home.html')
    
def about(request):
    return render(request, 'home/about.html')

def contact(request):
    if request.method=='POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        content = request.POST['content']
        print(name, email, phone, content)

        if len(name)<2 or len(email)<3 or len(phone)<10 or len(content)<4:
            messages.error(request, "Please fill the form correctly")
        else:
            contact = Contact(name=name, email=email, phone=phone, content=content)
            contact.save()
            messages.success(request, "Your messsage has been succesfully sent")

    return render(request, 'home/contact.html')


def search(request):
    query = request.GET['query']
    if len(query)>78:
        allPosts = Post.objects.none()
    else:
        allPostsTitle = Post.objects.filter(title__icontains=query)
        allPostsContent = Post.objects.filter(content__icontains=query)
        allPostsAuthor = Post.objects.filter(author__icontains=query)
        allPostsSlug = Post.objects.filter(slug__icontains=query)
        allPosts = allPostsTitle.union(allPostsContent, allPostsAuthor, allPostsSlug)

    if allPosts.count() == 0:
         messages.warning(request, "No search results found. Please refine your query")
    params = {'allPosts': allPosts, 'query':query}
    return render(request, 'home/search.html', params)

def handleSignup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Check for erronous inputs
        # username should be under 10 characters
        if len(username) > 10:
            messages.error(request, "Your username must be under 10 charecters")
            return redirect('home')

        # username should be alphanumeric
        if not username.isalnum():
            messages.error(request, "Your username should contain letters and numbers")
            return redirect('home')

        # password shoul match
        if pass1 != pass2:
            messages.error(request, "Your password do not match")
            return redirect('home')

        clientkey = request.POST['g-recaptcha-response']
        secretKey = '6LfkQuAZAAAAACY-Q0rIDEJ7THChWmvTt7WKEiEY'
        captchaData = {
            'secret': secretKey,
            'response': clientkey       
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=captchaData)
        response = json.loads(r.text)
        verify = response['success']
        print("Your success is here: ", verify)

        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your account has been succesfully created")
        return redirect('home')
    else:
        return HttpResponse('404 - Not Found')

def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']

        user = authenticate(username=loginusername, password=loginpassword)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect('home')
        else:
            messages.error(request, "Invalid Creadential, PLease try again")
            return redirect('home')


    return HttpResponse('404 - Not Found')

def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully Logged Out")
    return redirect('home')
        
    return HttpResponse('Handlelogout')
