$(document).ready(function(){
  $('.table-responsive').not(':eq(0)').slideUp();
  $('.tbltitle').click(function(){
    $(this).next('.table-responsive').slideToggle();
  })
})
