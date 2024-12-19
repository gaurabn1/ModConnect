from django.urls import path
#Password Reset Import#
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    #HomePage
    path('', views.home, name="home"),

    #Add Reply
    path('post/add-reply/<int:parent_id>', views.add_reply, name="add_reply") ,

    #Delete Comment Home
    path('post/delete-comment/<int:comment_id>/', views.delete_comment_home, name="delete_comment_home") ,

    #Delete Comment Profile
    path('delete-comment/<int:comment_id>/', views.delete_comment, name="delete_comment"),

    #Increment or Decrement Likes on Posts
    path('like-counter/', views.like_count, name="like-count"),

    #Login Users
    path('login/', views.login_page, name='login'),

    #Logout Users
    path('logout/', views.logout_page, name='logout'),

    #User Validation and Registration
    path('register/', views.register_page, name='register'),

    #Redirect to Profile Page
    path('profile/<pk>/', views.profile_page, name='profile'),

    #Retrieve Notifications
    path('notification/', views.notification, name='notification'),

    #Create Posts
    path('create-post/', views.create_post, name='create_post'),

    #Edit Posts
    path('edit-post/<int:postid>/', views.edit_post, name='edit_post'),

    #Create Notifications
    path('delete-post/<int:postid>/', views.delete_post, name='delete_post'),

    #Delete Notifications
    path('remove-notification/<int:id>/', views.remove_notification, name='remove_notification'),

    #Notification Mark as Read
    path('mark-as-read/<int:id>/', views.mark_as_read, name="mark_as_read"),

    #Delete Read Notifications
    path('clear-unread-notifications/', views.clear_all_unread_notifications, name="clear_all_unread_notifications"),

    #Delete Unread Notifications
    path('clear-read-notifications/', views.clear_all_read_notifications, name="clear_all_read_notifications"),

    #Follow Users
    path('follow-user/<int:userid>/', views.follow_user, name="follow_user"),
    
    # Search User
    path('search-user/<str:user>/', views.search_user, name="search_user"),

    #Comment
    path('post/comment/<str:post_id>/', views.comment_page, name='comment_page'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name = 'password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name= 'password_reset_done.html'), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name="password_reset_confirm"),
    path('reset/done/', auth_views.PasswordChangeDoneView.as_view(template_name = 'password_reset_complete.html'), name="password_reset_complete"),



    path('post/<int:post_id>/', views.post_comments, name="post_comments"),

    path('post/comment-delete/<int:comment_id>/', views.comment_delete, name="comment_delete") ,

        #Add Comment
    path('post/add-comment/<int:post_id>/', views.add_comment, name="add_comment"),

    path('post/comments/<int:post_id>/', views.more_comments, name="more_comments"),

    #Reply to Comments
    path('comments/<int:comment_id>/reply/', views.post_reply, name="post_reply"),

    path('post/comment/reply/<int:comment_id>/', views.get_replies, name="get_replies"),

    #Upload Profile Picture
    path('profile/image/upload/', views.profile_image_upload, name="profile_image_upload"),

    #Delete Profile Picture
    path('profile/image/delete/', views.delete_profile_image, name="delete_profile_image"),

]
