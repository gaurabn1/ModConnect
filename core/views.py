import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .utils import is_nsfw, blur_image, censor_text
from .models import *
from .forms import *

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

import threading
import numpy as np

from django.core.mail import EmailMessage
from django.conf import settings


MAX_COMMENT_LENGTH = 500

# ---------Homepage----------#
@login_required
def home(request):
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    posts = Post.objects.filter(author__in=following_users).order_by('?')[:10]    
    comment_form = CommentForm()
    users = CustomUser.objects.exclude(id=request.user.id).order_by('?')[:6]
    unread_notifications = Notification.objects.filter(user = request.user, is_read = False).exclude(created_by = request.user)
    count = unread_notifications.count()

    posts_with_like_status = []
    for post in posts:
        liked = post.likes.filter(id=request.user.id).exists()
        posts_with_like_status.append({
            'post': post,
            'liked': liked
        })

        for liked_post in posts_with_like_status:
            print("liked: ", liked_post)
   

    context = {
        'posts' : posts,
        'comment_form' : comment_form,
        'users' : users,
        'count' : count,
        'liked_post' : posts_with_like_status
    }
    return render(request, 'home.html', context)
# ---------Homepage End----------#

def serialize_comment(comment):
    return {
        'pk': comment.pk,
        'author_username': comment.author.username,
        'author_id': comment.author.id,
        'user_image': comment.author.image.url if comment.author.image else None,
        'censored_text': comment.censored_text,
    }

# -----------Add Comment----------------------#
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_text = comment_form.cleaned_data['text']

            if len(comment_text) > MAX_COMMENT_LENGTH:
                return JsonResponse({'error': f'Comment cannot exceed {MAX_COMMENT_LENGTH} characters.'}, status=400)            

            censored_text = censor_text(comment_text)
            # censored_text = censor_text(comment_text)

            mentioned_users = re.findall(r'@([a-zA-Z0-9_]+)', comment_text)
            mentioned_user_objs = []

            for username in mentioned_users:
                try:
                    user = get_object_or_404(CustomUser, username=username)
                    mentioned_user_objs.append(user)
                    
                    comment_text = re.sub(rf'@{username}', '', comment_text)
                    censored_text = re.sub(rf'@{username}', '', censored_text)
                except CustomUser.DoesNotExist:
                    continue  
            censored_text = ' '.join(censored_text.split())   

            for mentioned_user in mentioned_user_objs:
                Notification.objects.create(
                    user=mentioned_user,
                    message=f"You were mentioned in a comment by {request.user.username}: {censored_text}",
                    created_by=request.user,
                )         


            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post_id = post_id
            new_comment.censored_text = censor_text(new_comment.text)
            new_comment.save()

            message = f'{request.user.username} commented on your post'
            try:
                send_follow_email(f"Comment on your post", message, settings.EMAIL_HOST_USER, post.author.email)
            except:
                print("Email not sent")
            Notification.objects.create(user = post.author, message=message, created_by = request.user)

            post = get_object_or_404(Post, id=post_id)

            comments = post.comments.filter(post=post, parent=None).order_by('-created_at')[:5]
            comments_data = []
            for comment in comments:
                comments_data.append({
                    'id': comment.id,
                    'author': comment.author.id, 
                    'author_username': comment.author.username,
                    'author_id': comment.author.id,
                    'author_profile_image': comment.author.image.url if comment.author.image else '/static/images/avatar.jpg',
                    'censored_text': comment.censored_text,
                    'created_at': comment.created_at.isoformat(),  
                })


            return JsonResponse({'comments': comments_data, 'user_id': request.user.id})
        else:
            errors = comment_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)        
        
    else:
        return JsonResponse({'error' : 'Invalid Request'}, status = 405)
#-----------------Add Comment End---------------------------#

#-------------------Delete Comment Home---------------------#

def delete_comment_home(request, comment_id):
    comment = get_object_or_404(Comment, id = comment_id)
    comment.delete()
    return redirect('home')

#-----------------Delete Comment Home End---------------------#

#------------------Add Reply-------------------------------------#

def add_reply(request, parent_id):
    cmt = request.POST.get('text')
    print(cmt)
    if request.method == 'POST':
        parent_comment = get_object_or_404(Comment, id=parent_id)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.parent = parent_comment
            new_comment.post = parent_comment.post
            new_comment.censored_text = censor_text(new_comment.text)
            new_comment.save()


            serialized_comments = [serialize_comment(new_comment)]


            
            return JsonResponse({'comments': serialized_comments})
        else:
            errors = comment_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)        
        
    else:
        return JsonResponse({'error' : 'Invalid Request'}, status = 405)

#---------------Add Reply End-------------------------#


# ------------------Add Comment Profile Page-------------------------------------#
@login_required
def comment_page(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).order_by('-created_at')

    text = request.POST.get('text')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():

            comment_text = form.cleaned_data['text']
            # censored_text = censor_text(comment_text)
            censored_text = censor_text(comment_text)
            print("This is: ", censored_text)

            if len(comment_text) > MAX_COMMENT_LENGTH:
                return JsonResponse({'error': f'Comment cannot exceed {MAX_COMMENT_LENGTH} characters.'}, status=400)
            
            mentioned_users = re.findall(r'@([a-zA-Z0-9_]+)', comment_text)
            mentioned_user_objs = []

            for username in mentioned_users:
                try:
                    user = get_object_or_404(CustomUser, username=username)
                    mentioned_user_objs.append(user)
                    
                    comment_text = re.sub(rf'@{username}', '', comment_text)
                    censored_text = re.sub(rf'@{username}', '', censored_text)
                except CustomUser.DoesNotExist:
                    continue 

            # censored_text = ' '.join(censored_text.split())

            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.censored_text = censored_text
            comment.save()

            for mentioned_user in mentioned_user_objs:
                Notification.objects.create(
                    user=mentioned_user,
                    message=f"You were mentioned in a comment by {request.user.username}: {censored_text}",
                    created_by=request.user,
                )

            return redirect("comment_page", post_id )
    else:
        form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, 'comment.html', context)

# ------------------Add Comment Profile Page End-------------------------------------#

# ---------------------Delete Comment------------------------------#
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect('comment_page', comment.post.id)
    

# ---------------------Delete Comment End------------------------------#


# -------------Login View------------#
def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email = email, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            messages.info(request, 'Invalid Email or Password')
            return redirect('login')
    else:
        return render(request, 'login.html')

 
# -------------Login View End------------#

# ----------Logout--------------#
@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

# ----------Logout End--------------#


# -------------Register View------------#

def register_page(request):

    User = get_user_model()
    print("registered")

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')

        print("Email: ", email)
        print("Password: ", pass1)

        
        if User.objects.filter(username = username).exists():
            messages.info(request, "Username already exists!")
            return redirect('register')
        elif User.objects.filter(email = email):
            messages.info(request, "Email already exists.")
            return redirect('register')
        else:
            User.objects.create_user(username=username, email=email, password=pass1)
            messages.success(request, f"User {username} successfully registered")
            return redirect('login')
    return render(request, 'register.html')
# -------------Register View End------------#


# ---------------Profile Page---------------------#
@login_required
def profile_page(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    posts = Post.objects.filter(author = user)
    comment_form = CommentForm()

    following = Follow.objects.filter(follower = request.user, following = user)
    if following:
        is_following = True
    else:
        is_following = False
    context = {
        "posts" : posts,
        'user' : user,
        "comment_form" : comment_form,
        'is_following' : is_following
    }
    return render(request, "profile.html", context)

# ---------------Profile Page End---------------------#

#------------------Create Post-----------------#
@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        create_post = CreatePostForm(request.POST, request.FILES)
        if create_post.is_valid():
            new_post = create_post.save(commit=False)
            new_post.author = request.user

            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image_data = image_file.read() #read the image's binary data
                img = Image.open(BytesIO(image_data))   # Open the image with PIL (Python Imaging Library)
                
                img = img.convert('RGB') #convert the image into RGB Format
                
                img_array  = np.array(img) #convert the image into numpy array
                if is_nsfw(img_array):
                    blurred_img_array = blur_image(img_array) # Blur the Image if it is nsfw
                    
                    blurred_img = Image.fromarray(blurred_img_array.astype('uint8'))
                    print("blurred_img: ", blurred_img)
                    buffer = BytesIO()
                    blurred_img.save(buffer, format='JPEG')
                    blurred_image_name = f"blurred_{image_file.name}"
                    new_post.blurred_image.save(blurred_image_name, ContentFile(buffer.getvalue()), save=False)
                
                #Caption censorship
                caption = request.POST['caption']
                new_post.caption = censor_text(caption)



                new_post.save()
                return redirect('profile', user.id)
            else:
                create_post = CreatePostForm()
    else:
        create_post = CreatePostForm()


    context = {
        'create_post' : create_post
    }
    return render(request, 'create_post.html', context)

#------------------Create Post End-----------------#


#------------------Edit Post--------------------------#

def edit_post(request, postid):
    post = get_object_or_404(Post, id = postid)
    if request.method == "POST":
        form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('profile', request.user.id)
    else:
        form = EditPostForm(instance=post)

    context = {
        'post' : post,
        'form' : form
    }
    return render(request, 'edit_post.html', context)


#------------------Edit Post End--------------------------#


#------------------Delete Post-----------------#
def delete_post(request, postid):
    if request.method == "POST":
        post = get_object_or_404(Post, id = postid)
        post.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})



#------------------Delete Post End-----------------#


#------------------Like Counter----------------#
@login_required
def like_count(request):
    user = request.user
    if request.method == "POST":
        postid = request.POST.get('id')
        post = get_object_or_404(Post, id=postid)
        liked_user = post.author  # The user whose post is liked/unliked
        likes_user = get_object_or_404(CustomUser, email=user.email)  # Ensure we use email properly

        if not user in post.likes.all():  # If the user hasn't liked the post yet
            post.likes.add(user)
            liked = True
            message = f'{likes_user.username} likes your post'
            try:
                send_follow_email("Post Liked", message, settings.EMAIL_HOST_USER, liked_user.email)
            except:
                print("Email not sent")
            Notification.objects.create(user=liked_user, message=message, created_by=request.user)
        else:  # If the user has already liked the post
            post.likes.remove(user)
            liked = False
            message = f'{likes_user.username} unlikes your post'
            try:
                send_follow_email("Post Unliked", message, settings.EMAIL_HOST_USER, liked_user.email)
            except:
                print("Email not sent")
            Notification.objects.create(user=liked_user, message=message, created_by=request.user)

        post.save()  # Save post to update likes

        return JsonResponse({'message': message, 'liked': liked})

    return JsonResponse({"error": "Invalid Request"})
#------------------Like Counter End----------------#


#--------------Notification-----------------------------#
@login_required
def notification(request):
    '''
    Notification Page View
    '''
    unread_notification = Notification.objects.filter(user = request.user, is_read=False).exclude(created_by = request.user)
    read_notifications = Notification.objects.filter(user = request.user, is_read=True).exclude(created_by = request.user)
    count = unread_notification.count()
    
    context = {
        'unread_notification' : unread_notification,
        'count' : count,
        'read_notifications' : read_notifications,
        }
    return render(request, 'notification.html', context)


#--------------Notification End-----------------------------#

#---------------Remove Notification----------------#
@login_required
def remove_notification(request, id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=id)
        notification.delete()
        return redirect("notification")
    
#---------------Remove Notification End----------------#

#--------------Notification Mark As Read----------------#
@login_required
def mark_as_read(request, id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=id)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success" : "Notification Marked as read.."})
    return JsonResponse({"error" : "Invalid Request"})

#--------------Notification Mark As Read End----------------#

#-------------Clear All UnRead Notifications---------------------#

def clear_all_unread_notifications(request):
    if request.method == "POST":
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_notifications.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

#-------------Clear All UnRead Notifications End---------------------#


#-------------Clear All Read Notifications---------------------#

def clear_all_read_notifications(request):
    if request.method == "POST":
        read_notifications = Notification.objects.filter(user = request.user, is_read = True)
        read_notifications.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

#-------------Clear All Read Notifications End---------------------#


# Send Email #

def send_follow_email(subject, message, from_email, to_email):
    email = EmailMessage(subject, message, from_email, [to_email])
    email.fail_silently = False

    def email_send():
        try:
            email.send()
            print("Email Sent.")
        except Exception as e:
            print(f"Failed to send email: {e}")
        
    
    email_thread = threading.Thread(target=email_send)
    email_thread.start()


# Send Email End #


#---------------------Follow User-----------------------------#

def follow_user(request, userid):
    if request.method == "POST":
        user_to_follow = get_object_or_404(CustomUser, id=userid)
        user = request.user
        
        follow_instance, created = Follow.objects.get_or_create(follower = user, following = user_to_follow)

        if created:
            message = f'{user.username} follows you!'
            Notification.objects.create(user = user_to_follow, message = message)
            try:
                send_follow_email("Follow Added", message, settings.EMAIL_HOST_USER, user_to_follow.email)
            except:
                print("Email not sent")
        else:
            follow_instance.delete()
            message = f'{user.username} unfollows you!'
            try:
                send_follow_email("Follow Added", message, settings.EMAIL_HOST_USER, user_to_follow.email)
            except:
                print("Email not sent")

            Notification.objects.create(user = user_to_follow, message = message)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid Request'})

#---------------------Follow User End-----------------------------#

#--------------------Search Users---------------------------------#

def search_user(request, user):
    if request.method == "GET":
        users = CustomUser.objects.filter(username__startswith=user)
        
        if users.exists():
            users_list = list(users.values('id', 'username', 'first_name', 'last_name', 'image'))
            return JsonResponse({'users': users_list})
        else:
            return JsonResponse({'users': [], 'message': 'No users found matching the search.'})
    else:
        return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)

#--------------------Search Users End---------------------------------#






def post_comments(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        comments = post.comments.filter(post=post, parent=None).order_by('-created_at')[:5]
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment.id,
                'author': comment.author.id, 
                'author_username': comment.author.username,
                'author_id': comment.author.id,
                'author_profile_image': comment.author.image.url if comment.author.image else '/static/images/avatar.jpg',
                'text': comment.text,
                'censored_text': comment.censored_text,
                'created_at': comment.created_at.isoformat(),  
            })

        return JsonResponse({'comments' : comments_data, 'user_id' : request.user.id})
    
def comment_delete(request, comment_id):
    if request.method == 'POST':
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment.delete()
            return JsonResponse({'success': True, 'message': "Comment deleted successfully!"})
        except Comment.DoesNotExist:
            return JsonResponse({'error': 'Comment not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'success' : 'successfully done.'})


    
def more_comments(request, post_id):
    print(request.user)
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comments = Comment.objects.filter(post=post, parent=None).order_by('-created_at')
        comments_data = [
            {
                'id': comment.id,
                "author_id" : comment.author.id,
                'author': comment.author.username,
                'author_profile_image': comment.author.image.url if comment.author.image else '/static/images/avatar.jpg',
                'text': comment.censored_text,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for comment in comments
        ]        
        return JsonResponse({'comments' : comments_data, 'user_id' : request.user.id})
    

def post_reply(request, comment_id):
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text', '').strip()
        if not reply_text:
            return JsonResponse({'error': 'Reply text cannot be empty.'}, status=400)
        
        if len(reply_text) > MAX_COMMENT_LENGTH:
            return JsonResponse({'error': f'Comment cannot exceed {MAX_COMMENT_LENGTH} characters.'}, status=400)

        comment = get_object_or_404(Comment, id=comment_id)

        censored_text = censor_text(reply_text)

        mentioned_users = re.findall(r'@([a-zA-Z0-9_]+)', reply_text)
        mentioned_user_objs = []

        for username in mentioned_users:
            try:
                user = get_object_or_404(CustomUser, username=username)
                mentioned_user_objs.append(user)

                reply_text = re.sub(rf'@{username}', '', reply_text)
            except CustomUser.DoesNotExist:
                continue  
        reply_text = ' '.join(reply_text.split())

        censored_text = censor_text(reply_text)
        comment = get_object_or_404(Comment, id=comment_id)

        reply = Comment.objects.create(
            parent=comment,
            post=comment.post,
            author=request.user,
            text=reply_text,
            censored_text=censored_text
        )

        for mentioned_user in mentioned_user_objs:
            Notification.objects.create(
            user=mentioned_user, 
            message=f"You were mentioned in a reply by {request.user.username}: {censored_text}",
            created_by=request.user, 
        )

        return JsonResponse({
            'message': 'Reply posted successfully!',
            'id': reply.id,
            'author_id': reply.author.id,
            'author': reply.author.username,
            'text': censored_text,
            'image': comment.author.image.url if comment.author.image else '/static/images/avatar.jpg',
            'user_id': reply.author.id,
            'mentioned_users': [user.username for user in mentioned_user_objs] 
        })

def get_replies(request, comment_id):
    if request.method == 'GET':
        comment = Comment.objects.get(id=comment_id)
        replies = comment.replies.all()
        reply_data = [{
            'author' : reply.author.username,
            'author_id' : reply.author.id,  
            'text' : reply.censored_text,
            'id' : reply.id,
        }for reply in replies]
        return JsonResponse({'success': True, 'replies' : reply_data, 'user_id' : request.user.id})
    

def profile_image_upload(request):
    if request.method == 'POST':
        new_image = request.FILES.get('image')
        user = CustomUser.objects.get(id=request.user.id)
        user.image = new_image
        user.save()
        return JsonResponse({'success': True})
    
def delete_profile_image(request):
    if request.method == 'POST':
            if request.user.image:
                request.user.image.delete()
                return redirect('profile', request.user.id)
