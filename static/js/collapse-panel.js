  $(document).ready(function(){
    $('.panel-collapse').on('show.bs.collapse', function (ev) {
      $('.panel-collapse').removeClass('in');
    })

    showCollapsible();
  });

  $(window).resize(function(){
    showCollapsible();
  });
  
  function showCollapsible(){
    if ($(window).width() >= 767){  
      $('.panel-collapse').addClass('in');
    }
    if ($(window).width() <= 767){  
      $('.panel-collapse').removeClass('in');
    }
  }
