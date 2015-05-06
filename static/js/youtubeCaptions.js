  // ----------------- Global -----------------

$(function() {
  $main_container = $('.main_container');
  $input_panel = $('#input_panel');
  $input_form = $('#input_form');
  $query_input_field = $('.query_input_field');
  $error_text = $('.error_text');

  $info_panel = $('#info_panel');
  $results = $('#results')
  $map_canvas = $('#map-canvas');
  $spinner = $('#spinner');
  $result_count = $('#result_count');
  $display_input = $('#display_input');
  $back_button = $('#back_button');
  $results_button = $('#results_button');

});

// ------------------------ Functions ------------------------

$(document).ready(function () {

    var fill = d3.scale.category20();
    var color = d3.scale.linear()
            .domain([0,1,2,3,4,5,6,10,15,20,100])
            .range(["#ddd", "#ccc", "#bbb", "#aaa", "#999", "#888", "#777", "#666", "#555", "#444", "#333", "#222"]);

    var frequency_list = [{"text":"study","size":40},{"text":"motion","size":15},{"text":"forces","size":10}, {"text":"things","size":10},{"text":"force","size":5},{"text":"ad","size":5},{"text":"energy","size":85},{"text":"living","size":5},{"text":"nonliving","size":5},{"text":"laws","size":15},{"text":"speed","size":45},{"text":"velocity","size":30},{"text":"define","size":5},{"text":"constraints","size":5},{"text":"universe","size":10},{"text":"physics","size":120},{"text":"describing","size":5},{"text":"matter","size":90},{"text":"physics-the","size":5},{"text":"world","size":10},{"text":"works","size":10},{"text":"science","size":70},{"text":"interactions","size":30},{"text":"studies","size":5},{"text":"properties","size":45},{"text":"nature","size":40},{"text":"branch","size":30},{"text":"concerned","size":25},{"text":"source","size":40},{"text":"google","size":10},{"text":"defintions","size":5},{"text":"two","size":15},{"text":"grouped","size":15},{"text":"traditional","size":15},{"text":"fields","size":15}];


    d3.layout.cloud().size([400, 400])
            .words(frequency_list)
            .rotate(0)
            .fontSize(function(d) { return d.size; })
            .on("end", draw_words)
            .start();

    function draw_words(words) {
      var svg = d3.select('#stats').append('svg')
            .attr('height', 400)
            .attr('width', 400)
          .append('g')
            .attr('transform', 'translate(200, 200)')  
          .selectAll('words')
            .data(words)
          .enter().append('text')
            .style('font-size', function (d) {
              return d.size + 'px';
            })      
            .style('fill', function (d) {
              return '#F8F8F8';
            })
            .attr('text-anchor', 'middle')
            .attr('transform', function (d) {
              return 'translate(' + [d.x, d.y] + ')'; 
            })
            .text(function (d) {
              return d.text;
            })
    }

    // draw_words(frequency_list);

});

// ----------------- Event handlers -----------------


$(function() {
  $('#query_form').bind('submit', function() {
      console.log($('input[name="input"]').val());
      $.getJSON('./find_videos', {
        query: $('input[name="input"]').val(),
      }, function(data) {
        $("#stats").text(data.result);
      });
      console.log(":(");
      return false;
  });
});

// ------------------------ Styling ------------------------


$(document).ready(function () {
  $('.video').hover(
    function() {
      if ($(this).hasClass('selected')) {
        return;
      }
      else {        
        $(this).css('color', '#F8F8F8');
      }
    }, 
    function () {
      if ($(this).hasClass('selected')) {
        return;
      }
      else {
        $(this).css('color', '#ddcccc');
      }
    }
  );
  
  $('.video').click(
    function() {
      $('.selected').css('color', '#ddcccc');
      $('.selected').stop().animate({backgroundColor:'#cd201f'}, 400);
      $('.selected').removeClass('selected');

      $(this).addClass('selected');
      $(this).stop().animate({backgroundColor:'#F8F8F8'}, 400);
      $(this).css('color', '#383838');
      // $("#stats").html("Selected");
    }
  )
})

$(function(){
    $(window).resize(function(){
        var rankHeight = $('.rank').height();
        var scoreHeight = rankHeight/2;
        $('.score').css('height',scoreHeight + 'px');
    }).resize();    
});