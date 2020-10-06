function getCookie(name) {
 var cookieValue = null;
 if (document.cookie && document.cookie != '') {
     var cookies = document.cookie.split(';');
     for (var i = 0; i < cookies.length; i++) {
         var cookie = jQuery.trim(cookies[i]);
         if (cookie.substring(0, name.length + 1) == (name + '=')) {
             cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
         break;
     }
 }
 }
 return cookieValue;
}
var csrftoken = getCookie('csrftoken');


$('document').ready(function(){
    $('h6.likes').on('click', function(){
        let comment_id = $(this).attr('id')
        let obj = this
        $.ajax({
            url: "/shop/add_ajax_comment/",
            method: 'post',
            data : {"comment_id": comment_id, "csrfmiddlewaretoken": csrftoken},
            success: function(data){
                $(obj).html(` Likes: ${data['likes']}`)
                if (data['flag']){
                    $(obj).attr('class', 'rate fa fa-star checked')
                }else{
                    $(obj).attr('class', 'rate fa')
                }
            }
        })
    })

    $('span.rate').on('click', function(){
        let rate_id = $(this).attr("id").slice(4)
        $.ajax({
            url: "/shop/add_ajax_rate/",
            method: 'post',
            data : {"rate_id": rate_id, "csrfmiddlewaretoken": csrftoken},
            success: function(data){
                let book_id = rate_id.split('-')[0]
                $(`#book_rate${book_id}`).html(`Rate: ${data['rate']}`)
                for (let i = 1; i < 6; i++) {
                        if (i <= data['stars']){
                            $(`#book${book_id}-${i}`).attr('class', 'rate fa fa-star checked')
                        }else{
                            $(`#book${book_id}-${i}`).attr('class', 'rate fa fa-star')}
                     }
            }
        })
    })

    $('button.delete_book').on("click", function(){
        let book_id = $(this).attr('id')
        $.ajax({
            url: `/shop/delete_ajax_book/${book_id}/`,
            headers: { 'X-CSRFToken': csrftoken },
            method: 'delete',
            success: function(data){
                    $(`div#book${data['slug']}`).remove()
            }
        })
    })

    $('button.delete-comment').on('click', function(){
        let comment_id = $(this).attr('id').split('-')[2]
        $.ajax({
            url: `/shop/delete_ajax_comment/${comment_id}/`,
            headers: { 'X-CSRFToken': csrftoken },
            method: 'delete',
            success: function(data){
                if(data['delete']){$(`div#comment-container-${comment_id}`).remove()}
            }
        })
    })
})