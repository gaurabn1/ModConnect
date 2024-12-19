
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// ------------- get csrf token End--------------------//

function deleteComment(commentId) {
    if (confirm('Are you sure you want to delete this comment?')) {
        $.ajax({
            type: 'POST',
            url: `/post/comment-delete/${commentId}/`,
            headers: {
                "X-CSRFToken": getCookie('csrftoken'),
            },
            success: function(res) {
                if (res.success) {
                    // Remove the comment from the DOM
                    $(`#comment-${commentId}`).remove();
                    alert('Comment deleted successfully');
                } else {
                    alert('Error deleting comment');
                }
            }
        });
    }
}




// Add Comment on Posts

$(document).ready(function () {

    $('a[id^="commentIcon-"]').on('click', function (e) {
        e.preventDefault();
        $('#rightSidebar').css('display', 'none'); 
        let postId = $(this).data('post-id');
        $.ajax({
            type: 'POST',
            url: `/post/${postId}/`, 
            headers: {
                "X-CSRFToken": getCookie('csrftoken')
            },
            data: {
                'post_id': postId
            },
            success: function (res) {

                let commentsHtml = '';
            
                if (res.comments && res.comments.length > 0) {
                    commentsHtml = `
                    <div class="recent-comments-header" style="font-size: 1.5rem; font-weight: bold; color: white; padding: 10px 0;">
                        Recent Comments
                    </div>`; 
            
                    res.comments.forEach(function (comment) {
                        commentsHtml += `
                        <div class="comment-card mb-4 p-3" style="background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;" id="comment-${comment.id}">
                            <div class="d-flex align-items-center">
                                <!-- Profile Image -->
                                <div class="profile-image mr-3">
                                    <img src="${comment.author_profile_image || 'default-avatar.jpg'}" class="rounded-circle" height="40px" width="40px" alt="">
                                </div>
            
                                <!-- Comment Details -->
                                <div class="mx-3">
                                    <p class="mb-1">
                                        <a href="/profile/${comment.author_id}" style="color: #c8c8c8; text-decoration: none; font-weight: 500;">
                                            ${comment.author_username || 'Unknown'}
                                        </a>
                                    </p>
                                    <small style="color: #afacac; font-style: italic;">${comment.censored_text}</small><br>
                                    <small class="text-secondary mx-3"><a href="" class="reply-link" data-comment-id="${comment.id}">reply</a></small>
            
                                    ${comment.author === res.user_id ? `
                                        <small class="text-danger" style="cursor: pointer;" onclick="deleteComment(${comment.id})">delete</small>
                                    ` : ``}
                                </div>
                            </div>  
                        </div>
                        `;
                    });

                    commentsHtml += `
        <div class="text-center">
            <button id="more_comments" class="btn btn-secondary btn-sm" style="width: 100%; border-radius: 8px;" data-post-id="${postId}">View All Comments</button>
        </div>`;

        } else {
                    // If no comments, display a message
                    commentsHtml = `
                    <div class="no-comments-message" style="padding: 20px; text-align: center; color: white;">
                        No comments yet. Be the first to comment!
                    </div>
                    `;
                }
            
                $('#rightSidebar').html(commentsHtml);
                $('#rightSidebar').css('display', 'block');  
            }
            
        });
    });


    // Post Comment
$('button[id^="post_comment-"]').on('click', function (e) {
    e.preventDefault();
    let post_id = $(this).data('post-id');
    let comment_text = $(`#comment_form-${post_id} textarea[name='text']`).val();

    $.ajax({
        type: 'POST',
        url: `/post/add-comment/${post_id}/`,
        headers: {
            "X-CSRFToken": getCookie('csrftoken')
        },
        data: {
            'post_id': post_id,
            'text': comment_text,
        },
        success: function (res) {
            if (res.comments) {
                let commentsHtml = `
                    <div class="recent-comments-header" style="font-size: 1.5rem; font-weight: bold; color: white; padding: 10px 0;">
                        Recent Comments
                    </div>`; 

                res.comments.forEach(function (comment) {
                    commentsHtml += `
                        <div class="comment-card mb-4 p-3" style="background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;" id="comment-${comment.id}">
                            <div class="d-flex align-items-center">
                                <!-- Profile Image -->
                                <div class="profile-image mr-3">
                                    <img src="${comment.author_profile_image || 'default-avatar.jpg'}" class="rounded-circle" height="40px" width="40px" alt="">
                                </div>
            
                                <!-- Comment Details -->
                                <div class="mx-3">
                                    <p class="mb-1">
                                        <a href="/profile/${comment.author_username}" style="color: #c8c8c8; text-decoration: none; font-weight: 500;">
                                            ${comment.author_username || 'Unknown'}
                                        </a>
                                    </p>
                                    <small style="color: #afacac; font-style: italic;">${comment.censored_text}</small><br>
                                    <small class="text-secondary mx-3"><a href="" class="reply-link" data-comment-id="${comment.id}">reply</a></small>

                                    ${comment.author === res.user_id ? `
                                        <small class="text-danger" style="cursor: pointer;" onclick="deleteComment(${comment.id})">delete</small>
                                    ` : ``}
                                </div>
                            </div>  
                        </div>
                    `;
                });

                commentsHtml += `
                    <div class="text-center">
                        <button id="more_comments" class="btn btn-secondary btn-sm" style="width: 100%; border-radius: 8px;" data-post-id="${post_id}">View All Comments</button>
                    </div>`;

                $('#rightSidebar').html(commentsHtml);
                $('#rightSidebar').css('display', 'block');

                $(`#comment_form-${post_id} textarea[name='text']`).val('');
            } else {
                console.error("No comments returned or error occurred.");
            }
        },
        error: function(xhr, status, error) {
                alert(xhr.responseJSON.error);  
            
        }
    });
});


    //Show All Comments

    $(document).on('click', "#more_comments", function(){
        let postId = $(this).data('post-id')

        
        $.ajax({
            type: "POST",
            url: `/post/comments/${postId}/`,
            headers: {
                'X-CSRFToken' : getCookie('csrftoken')
            },
            success: function (res) {
                if (res.comments && res.comments.length > 0) {
                    let commentsHtml = `
                    <div class="recent-comments-header" style="font-size: 1.5rem; font-weight: bold; color: white; padding: 10px 0;">
                        Recent Comments
                    </div>`;
    
                    res.comments.forEach(function (comment) {
                        commentsHtml += `
                        <div class="comment-card mb-4 p-3" style="background-color: rgba(255, 255, 255, 0.1); border-radius: 8px;" id="comment-${comment.id}">
                            <div class="d-flex align-items-center">
                                <!-- Profile Image -->
                                <div class="profile-image mr-3">
                                    <img src="${comment.author_profile_image || 'default-avatar.jpg'}" class="rounded-circle" height="40px" width="40px" alt="">
                                </div>
    
                                <!-- Comment Details -->
                                <div class="mx-3">
                                    <p class="mb-1">
                                        <a href="/profile/${comment.author_id}" style="color: #c8c8c8; text-decoration: none; font-weight: 500;">
                                            ${comment.author || 'Unknown'}
                                        </a>
                                    </p>
                                    <small style="color: #afacac; font-style: italic;">${comment.text}</small><br>
                                    <small class="text-secondary mx-3"><a href=""  class="reply-link" data-comment-id="${comment.id}">reply</a></small>
    
                                    ${comment.author_id === res.user_id ? `
                                        <small class="text-danger" style="cursor: pointer;" onclick="deleteComment(${comment.id})">delete</small>
                                    ` : ``}
                                </div>
                            </div>  
                        </div>
                        `;
                    });
    
                    $('#rightSidebar').html(commentsHtml);
    
                } else {
                    // If no more comments, show a message
                    $('#rightSidebar').html(`
                        <div class="no-comments-message" style="padding: 20px; text-align: center; color: white;">
                            No more comments available.
                        </div>
                    `);
                }
            },
        })
    })


    //Reply to Comments
    $(document).on('click', ".reply-link", function (e) {
        e.preventDefault();
    
        let commentId = $(this).data('comment-id');
    
        let replyContainer = $(`#replies-${commentId}`);
        let replyForm = $(`#replyForm-${commentId}`);
        
        if (replyForm.length && replyForm.is(":visible")) {
            replyForm.remove();
            replyContainer.hide();
        } else {
            $.ajax({
                type: 'GET',
                url: `/post/comment/reply/${commentId}/`,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                success: function (res) {
                    if (!replyContainer.length) {
                        let repliesHtml = res.replies.map(function(reply) {

                            let isAuthor = reply.author_id === res.user_id;
                            return `
                                <div class="reply-card mb-2" data-comment-id="${reply.id}" id="comment-${reply.id}" style="background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px;">
                                <div style="display:flex; justify-content: space-between;">
                                    <small><strong><a href="/profile/${reply.author_id}">${reply.author}</a></strong>: ${reply.text}</small>
                                
                                ${isAuthor ? `
                                    <small class="text-danger" style="cursor: pointer;" onclick="deleteComment(${reply.id})">delete</small>
                                ` : ''}
                                </div>
                            </div>
                            `;
                        }).join('');
    
                        replyContainer = $(`
                            <div class="replies" id="replies-${commentId}">
                                ${repliesHtml}
                            </div>
                        `).hide();
    
                        $(`#comment-${commentId}`).append(replyContainer);
                    }
                    replyContainer.show(); 
    
                    let replyFormHtml = `
                        <div class="reply-form mt-2" id="replyForm-${commentId}">
                            <textarea class="form-control reply-text" rows="2" placeholder="Write your reply..." style="background-color: rgba(255, 255, 255, 0.1); color: white;"></textarea>
                            <button class="btn btn-sm btn-primary mt-2 post-reply-btn" data-comment-id="${commentId}">Post Reply</button>
                            <button class="btn btn-sm btn-secondary mt-2 cancel-reply-btn" data-comment-id="${commentId}">Cancel</button>
                        </div>
                    `;
                    $(`#comment-${commentId}`).append(replyFormHtml);
                }
            });
        }
    });
    
    
    
    $(document).on('click', ".post-reply-btn", function () {
        let commentId = $(this).data('comment-id');
        let replyText = $(`#replyForm-${commentId} .reply-text`).val();
    
        if (!replyText.trim()) {
            alert("Reply cannot be empty.");
            return;
        }
    
        $.ajax({
            type: "POST",
            url: `/comments/${commentId}/reply/`, 
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            data: {
                'reply_text': replyText
            },
            success: function (res) {
                let isAuthor = res.author_id === res.user_id;
                let newReplyHtml = `
                   <div class="reply-card mb-2" data-comment-id="${res.id}" id="comment-${res.id}" style="background-color: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 8px;">
                                <div style="display:flex; justify-content: space-between;">
                                    <small><strong>${res.author}</strong>: ${res.text}</small>
                                
                                ${isAuthor ? `
                                    <small class="text-danger" style="cursor: pointer;" onclick="deleteComment(${res.id})">delete</small>
                                ` : ''}
                                </div>
                            </div>
                `;
    
                if ($(`#replies-container-${commentId}`).length === 0) {
                    $(`#comment-${commentId}`).append(`<div id="replies-container-${commentId}" class="ml-4"></div>`);
                }
    
                $(`#replies-container-${commentId}`).append(newReplyHtml);
                $(`#replyForm-${commentId} .reply-text`).val(''); // Clear the textarea
            },
            error: function (xhr, err) {
                    alert(xhr.responseJSON.error);  
            }
        });
    });

    $(document).on('click', ".cancel-reply-btn", function () {
        let commentId = $(this).data('comment-id');
        $(`#replyForm-${commentId}`).remove();
    });
    

  
 

});

//   Logout

$('.option').on('click', 'a:not(#logout)', function (e) {
    e.preventDefault();
    $('.option a').removeClass('active');
    $(this).addClass('active');
    window.location.href = $(this).attr('href');
});


// -------------Update Like on Own Page------------//
$(document).ready(function () {
    $(".like-button").on('click', function (e) {
        e.preventDefault();
        
        var postid = $(this).data('post-id');
        var likeCounter = $(this).closest('.interact').find('.like-counter');
        var likeButton = $(this);
        var likedIcon = likeButton.find(".liked-icon");
        var unlikedIcon = likeButton.find(".unliked-icon");
        var likes = parseInt(likeCounter.text());

        // Disable the like button while the request is processing
        likeButton.prop('disabled', true);

        $.ajax({
            type: "POST",
            url: '/like-counter/',
            data: {
                "id": postid
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            success: function (response) {
                if (response.liked) {
                    likes += 1;
                    likedIcon.show();
                    unlikedIcon.hide();
                } else {
                    likes -= 1;
                    likedIcon.hide();
                    unlikedIcon.show();
                }

                // Update like counter
                likeCounter.text(likes);

                // Re-enable the like button after processing
                likeButton.prop('disabled', false);
            },
            error: function (xhr, status, error) {
                console.log(xhr, " ", status);
                likeButton.prop('disabled', false);
            }
        });
    });
});

// ---------Update Like on Page End--------------------//



//---------------Logout----------------------//
$('#logout').click(function (e) {
    e.preventDefault();
    if (!confirm("Are you sure?")) {

    }
    else {
        window.location.href = '/logout/';
    }
    //---------------Logout End----------------------//

});

//---------------------Search Form------------------------//

$('#searchFormButton').on('click', function (e) {
    e.preventDefault();
    search_user = $('#searchField').val();

    $.ajax({
        url: `/search-user/${search_user}/`,
        type: 'GET',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: function (response) {
            $('.search-results').empty();
            if (response.users.length > 0) {
                $.each(response.users, function (index, user) {
                    let profileUrl = `/profile/${user.id}/`
                    let imageUrl = user.image ? `/media/${user.image}` : '/static/images/avatar.jpg';
                    let imageHtml = `<img src="${imageUrl}" alt="Profile Image" class="rounded-circle" style="width: 40px; height: 40px; margin-right: 10px;">`;                    
                    if (user.first_name) {
                        $('.search-results').append(
                            `<a href="${profileUrl}" ><div style="display: flex; align-items: center; height: 50px">${imageHtml}<p>${user.first_name} ${user.last_name}</p></div></a>`                        
                        )
                    } else if (user.username) {
                        $('.search-results').append(
                            `<a href="${profileUrl}"><div style="display: flex; align-items: center;">${imageHtml}<p class="text-capitalize">${user.username}</p></div></a>`                        
                        )
                    }
                })
            } else {
                $('.search-results').append('<p> Users not found.</p>');
            }
        }
    })
})


//---------------------Search Form End------------------------//





