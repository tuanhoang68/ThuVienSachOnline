from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.core.mail import send_mail

from .models import *
from .forms import *


# Create your views here.
def register (request):
    # Đã đăng nhập thì không mở page Login/Register được
    if request.user.is_authenticated:
        return redirect('userHome')
    else:
        form = CreateUserForm()
        
        if request.method == "POST":
            
            #Mật khẩu quá ngắn (< 8 ký tự)
            pass_0 = request.POST.get('password1')
            if(len(pass_0) < 8):
                messages.error(request, 'Mật khẩu ngắn hơn 8 ký tự!')
                return redirect('register')  
            
            #Không trùng mật khẩu
            pass_1 = request.POST.get('password1')
            pass_2 = request.POST.get('password2')
            if pass_1 != pass_2:
                messages.error(request, 'Mật khẩu không khớp nhau!')
                
                return redirect('register')  
            
            #Log thông báo trùng username
            users = User.objects.all()
            for user in users:
                username_X = request.POST.get('username')
                if user.username == username_X:
                    messages.error(request, 'Tên đăng nhập đã tồn tại!')
                        
                    return redirect('register')   
            
            #Username hợp lệ
            form = CreateUserForm(request.POST)
            
            if form.is_valid():
                
                
                form.save()
                
                username = form.cleaned_data.get('username')
                messages.success(request, 'Đã tạo người dùng ' + username + ' thành công!')
                
                return redirect('login')
                
        context = {'form': form}
        return render(request, 'authenticationPages/register.html', context)


def login (request):
    # Đã đăng nhập thì không mở page Login/Register được
    if request.user.is_authenticated:
        return redirect('userHome')
    else:
        if request.method == "POST":
            #Nhập thiếu trường
            print(request.POST)
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username = username, password = password)
            
            if user is not None:
                auth_login(request, user)
                return redirect('http://localhost:8000/userhome/')
            else:
                messages.error(request, "Thông tin đăng nhập không chính xác!")
                
        context = {}
        return render(request, 'authenticationPages/login.html', context)



def logOut(request):
    auth_logout(request)
    return redirect('http://localhost:8000/')


def getGuestHome (request):
    books = Book.objects.all()
    
    return render( request, "guestPages/guestHome.html", {'books' : books})


@login_required(login_url='login/')
def getUserHome (request):
    books = Book.objects.all()
    
    return render( request, "userPages/userHome.html", {'books' : books})


@login_required(login_url='/login/')
def addBook (request):
    form = addBookForm()
    
    # print(request.user.email)
    
    form.fields['release_date'].widget.input_type = 'datetime-local'
    form.fields['release_date'].required = True
    
    if request.method == "POST":
        
        # Tiêu đề sách đã tồn tại
        books = Book.objects.all()
        booknameX = request.POST.get('name')
        for book in books:
            if book.name == booknameX:
                messages.error(request, 'Tiêu đề sách đã tồn tại!')
                return redirect('addBook') 
        
        
        form = addBookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            print("Thêm sách thành công.")
            book = Book.objects.last()
            
            if not book.image:
                Book.objects.filter(id=book.id).update(image='default_image.jpg')
            
            return redirect('http://localhost:8000/viewBook/' + str(book.id) +'/')
        else:
            messages.error(request, "Định dạng ảnh không đúng!")
        
    context = {'form' : form}
    
    return render(request, 'userPages/addBook.html', context)


@login_required(login_url='/login/')
def viewBook (request, pk):
    book = Book.objects.get(id = pk)
    form = addBookForm(instance = book)     
    
    form.fields['name'].disabled = True
    form.fields['author'].disabled = True
    form.fields['description'].disabled = True
    form.fields['category'].disabled = True
    form.fields['release_date'].disabled = True
    form.fields['number_of_pages'].disabled = True
    form.fields['image'].disabled = True
    
    context = {'form' : form, 'book': book}
    
    return render(request, 'userPages/viewBook.html', context)


@login_required(login_url='/login/')
def editBook (request, pk):
    book = Book.objects.get(id = pk)
    
    form = addBookForm(instance = book)
    
    form.fields['release_date'].widget.input_type = 'datetime-local'
    
    form.fields['name'].disabled = False
    form.fields['author'].disabled = False
    form.fields['description'].disabled = False
    form.fields['category'].disabled = False
    form.fields['release_date'].disabled = False
    form.fields['number_of_pages'].disabled = False
    form.fields['image'].disabled = False
    
    if request.method == "POST":
        form = addBookForm(request.POST, request.FILES, instance = book)
        
        if form.is_valid():
            form.save()
            
            return redirect('http://localhost:8000/viewBook/' + str(book.id) +'/')
        
    context = {'form' : form, 'book': book}
    
    
    return render(request, 'userPages/editBook.html', context)



@login_required(login_url='/login/')
def deleteBook (request, pk):
    
    book = Book.objects.get(id = pk)
        
    book.delete()
    return redirect('http://localhost:8000/userhome/')
        
        
        
        
@login_required(login_url='/login/')
def statisticalBook (request):
    categories = Book.objects.values('category').distinct()
    cate = []
    count = []
    for category in categories:
        x = category['category']
        if x is not None:
            cate.append(x)
        else: 
            cate.append('Chưa chọn thể loại')
        
        amount_book = len(Book.objects.filter(category = category['category']))
        count.append(amount_book)
    print(cate)
    print(count)
    context = {
        "category" : cate,
        "amount"   : count
    }
    print(context)
    return render(request, 'userPages/statisticalBook.html', context)


@login_required(login_url='/login/')
def profileUser (request):
    user = request.user
    # user = {
    #     'last_name': request.user.last_name,
    #     'first_name': request.user.first_name,
    #     'email': request.user.email,
    # }
    # print(type(user))
    # print(user)
    
    form = profileUserForm(instance = user)
    print("FORM profileUser: ", form)
    # print(form)
    # form.fields['username'].disabled = True
    form.fields['email'].disabled = True  
    form.fields['first_name'].disabled = True  
    form.fields['last_name'].disabled = True  
    
    context = {'form': form}
    return render(request, 'userPages/profileUser.html', context)

@login_required(login_url='/login/')
def editUser (request):
    
    user = request.user
    # print(user.password)
    
    form = profileUserForm(instance = user)
    print(form)
    
    form.fields['email'].disabled = False  
    form.fields['first_name'].disabled = False  
    form.fields['last_name'].disabled = False  
    
    #START
    if request.method == "POST":
        form = profileUserForm(request.POST, instance = user)
        
        print('------------------')
        print(request.POST)
        
        if form.is_valid():
            form.save()
            print('------------------')
            username = request.user.username
            messages.success(request, 'Chỉnh sửa người dùng ' + str(username) + ' thành công!')
            
            return redirect('profileUser')
    
    context = {'form': form}
    return render(request, 'userPages/editUser.html', context)


@login_required(login_url='/login/')
def sendMail (request):
    user = request.user
    
    form = sendMailForm(instance = user)
    form.fields['email'].disabled = True   
    
    #START
    if request.method == "POST":
        
        import random
        Key_part_1 = random.randrange(100, 999, 1)
        Key_part_2 = random.randrange(100, 999, 1)
        key = str(Key_part_1) + str(Key_part_2)
        
        request.session['num'] = key
        
        msg = "Mã khôi phục mật khẩu: " + key
        print("MSG: ", msg)
        
        email = user.email
        # Gửi mail
        
        # send_mail(
        #     '[Thuviensachonline.com] KHÔI PHỤC MẬT KHẨU!',
        #     msg,
        #     'abc@gmail.com',
        #     [email],
        #     fail_silently=True,
        # )
    
        
        return render(request, 'userPages/confirmCodeMail.html')
            
             
    context = {'form': form}
    return render(request, 'userPages/sendMail.html', context)



@login_required(login_url='/login/')
def confirmCodeMail (request):
    key = request.session.get('num')
    print("KEYYYYY: ", key)
    user = request.user
    print("AAAAAAAAAAAAAAAAAA")
    # email = user.email
    form = confirmCodeMailForm()
    
    # form.fields['email'].disabled = True   
    
    #START
    if request.method == "POST":
        print(request.POST)
        context = {
            'form' : form,
        }
        return render(request, 'userPages/resetPassword.html', context)
    
    
    context = {'form': form}
    return render(request, 'userPages/confirmCodeMail.html', context)  


@login_required(login_url='/login/')
def resetPassword (request):
    user = request.user
    
    email = user.email
    
    form = profileUserForm(instance = user)
    print(form)
    
    form.fields['email'].disabled = True   
    
    #START
    if request.method == "POST":
        
        form = profileUserForm(request.POST, instance = user)
        
        print('------------------')
        print(request.POST)
        
        if form.is_valid():
            key = "123456"
            msg = "Mã khôi phục mật khẩu: " + key
            
            send_mail(
                'Khôi phục mật khẩu',
                msg,
                'abc@gmail.com',
                [email],
                fail_silently=True,
            )
            
            username = form.cleaned_data.get('username')
            messages.success(request, 'Chỉnh sửa người dùng ' + username + ' thành công!')
            
            return redirect('profileUser')
    
    context = {'form': form}
    return render(request, 'userPages/resetPassword.html', context)      