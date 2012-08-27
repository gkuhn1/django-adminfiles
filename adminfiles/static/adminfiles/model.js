(function($) {
$(function(){
    $('.adminfilespicker').each(function(){
            var widget = $(this).find('.adminfilespicker-widget').first();
            var browser = $(this).find('.adminfilespicker-browser').first();
            var iframe = $(this).find('iframe').first();
            trigger = $(this).find('.adminfilespicker-trigger').first();

            var href = '/adminfiles/all/?field='+widget.attr('id');

            if (widget.options) {
                widget.siblings('a.add-another').remove();
                href += '&field_type=select';
            }
            trigger.attr('href', href).fancybox({
                  type: 'iframe',
                  href: href,
                  width: '80%',
                  height: '80%',
                  autoDimensions: false
                });
            // iframe.attr('src', href);
       });
    });
})(jQuery);
