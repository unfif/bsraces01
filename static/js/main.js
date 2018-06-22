$(document).ready(function(){
  // $('.table-responsive').not(':eq(0)').slideUp();
  $('.disptgl').hide().removeClass('hidden');

  $('.tbltitle').click(function(){
    // $(this).next('.table-responsive').slideToggle();
    $(this).siblings('.table-responsive').find('.disptgl').fadeToggle();
  })
})
