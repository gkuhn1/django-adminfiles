(function($) {
     $(function(){
           $('.adminfilespicker').each(
               function(){
                   var href = '/adminfiles/all/?field='+this.id;
                   if (this.options) {
                   $(this).siblings('a.add-another').remove();
                   href += '&field_type=select';
	           }
               var size = $(this).attr('data-size').split('x');
               $(this).after('<a id="add-file-'+$(this).attr('id')+'" class="addlink">Add File</a>');
               $('#add-file-'+$(this).attr('id')).click(function() {
                   $(this).after('<br><iframe frameborder="0" style="border:none; width:'+size[0]+'px; height:'+size[1]+'px;" src="' + href + '"></iframe>');
               });
	       });
       });
 })(jQuery);
