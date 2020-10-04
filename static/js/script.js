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
            headers: { 'X-CSRFToken': csrftoken },
            method: 'post',
            data : {"comment_id": comment_id},
            success: function(data){
                $(obj).html(" Likes: " + data['likes'])
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
            headers: { 'X-CSRFToken': csrftoken },
            method: 'post',
            data : {"rate_id": rate_id},
            success: function(data){
                let book_id = rate_id.split('-')[0]
                $('#book_rate' + book_id).html('Rate: ' + data['rate'])
                for (let i = 1; i < 6; i++) {
                        if (i <= data['stars']){
                            $('#book' + book_id + "-" + i).attr('class', 'rate fa fa-star checked')
                        }else{
                            $('#book' + book_id + "-" + i).attr('class', 'rate fa fa-star')}
                     }
            }
        })
    })

    $('button.delete_book').on("click", function(){
        let book_id = $(this).attr('id')
        let btn = this
        $.ajax({
            url: '/shop/delete_ajax_book/',
            headers: { 'X-CSRFToken': csrftoken },
            method: 'delete',
            data: {'book_id': book_id},
            success: function(data){
                if(data['flag']){
                    $('div#book' + data['slug']).remove()
                }else{
                    $(btn).attr('style', 'color:red')
                }
            }
        })
    })

})