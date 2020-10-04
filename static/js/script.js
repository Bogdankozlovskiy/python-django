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
    $('.likes').on('click', function(){
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

    $('.rate').on('click', function(){
        let rate_id = $(this).attr("id")
        $.ajax({
            url: "/shop/add_ajax_rate/",
            headers: { 'X-CSRFToken': csrftoken },
            method: 'post',
            data : {"rate_id": rate_id},
            success: function(data){
                console.log(data)
            }
        })
    })
})