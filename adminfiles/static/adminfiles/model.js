(function($) {
$(function(){
    $('.adminfilespicker').each(function(){
            var widget = $($(this).find('.adminfilespicker-widget')[0]);
            var browser = $($(this).find('.adminfilespicker-browser')[0]);
            var iframe = $($(this).find('iframe')[0]);
            var trigger = $($(this).find('.adminfilespicker-trigger')[0]);

            var href = '/adminfiles/all/?field='+widget.attr('id');

            if (widget.options) {
                widget.siblings('a.add-another').remove();
                href += '&field_type=select';
            }

            trigger.click(function() {
                browser.toggle();
            });
            iframe.attr('src', href);
       });
    });
})(jQuery);
