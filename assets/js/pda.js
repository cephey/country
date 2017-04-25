$(function(){
    $('#desktop_version').on('click', function() {
        document.cookie = 'desktop_version=1; path=/';
    });
});