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


var fill = d3.scale.category20();
var color = d3.scale.linear()
        .domain([0,1,2,3,4,5,6,10,15,20,100])
        .range(["#ddd", "#ccc", "#bbb", "#aaa", "#999", "#888", "#777", "#666", "#555", "#444", "#333", "#222"]);

var frequency_list = [{"text":"study","size":40},{"text":"motion","size":15},{"text":"forces","size":10}, {"text":"things","size":10},{"text":"force","size":5},{"text":"ad","size":5},{"text":"energy","size":85},{"text":"living","size":5},{"text":"nonliving","size":5},{"text":"laws","size":15},{"text":"speed","size":45},{"text":"velocity","size":30},{"text":"define","size":5},{"text":"constraints","size":5},{"text":"universe","size":10},{"text":"physics","size":120},{"text":"describing","size":5},{"text":"matter","size":90},{"text":"physics-the","size":5},{"text":"world","size":10},{"text":"works","size":10},{"text":"science","size":70},{"text":"interactions","size":30},{"text":"studies","size":5},{"text":"properties","size":45},{"text":"nature","size":40},{"text":"branch","size":30},{"text":"concerned","size":25},{"text":"source","size":40},{"text":"google","size":10},{"text":"defintions","size":5},{"text":"two","size":15},{"text":"grouped","size":15},{"text":"traditional","size":15},{"text":"fields","size":15}];

function draw_words(words) {
  d3.select('#stats').html("");
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

function render_wordcloud(words) {
  d3.layout.cloud().size([400, 400])
            .words(words)
            .rotate(0)
            .fontSize(function(d) { return d.size; })
            .on("end", draw_words)
            .start();
}

function render_results(scores, thumbnails, descriptions, titles, urls) {
  var result = '';

  for (var x = 0; x < scores.length; x++) {
    result += '<div id="' + urls[x] + '" class="row bottom-margin video">' +
                  '<div class="col-md-2">' + 
                      'Rank' +
                      '<div class="rank">' + (x + 1).toString() + '</div>' +
                  '</div>' +
                  '<div class="col-md-2">' +
                      'Score' +
                      '<div class="score"><span> + ' + scores[x] + '</span></div>' +
                  '</div>' +
                  '<div class="col-md-5">' +
                    '<a class="link" target="_blank" href="https://www.youtube.com/watch?v=' + urls[x] + '">' +
                      '<img class="thumbnail"' + 'src="' + thumbnails[x] + '"/>' +
                    '</a>' +
                  '</div>' + 
                  '<div class="col-md-3 left-text">' + 
                    titles[x] + '<br/><br/>' + descriptions[x] + 
                  '</div>' +
              '</div>';
  }

  $('#left').html(result);
  
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
        
        // Get information
        document.getElementById('loading-info').style.display='block';
        var id = $(this).attr('id');
        $.getJSON('./get_info', {
          video: $(this).attr('id'),
        }, function(data) {
          render_wordcloud(data.words);
          document.getElementById('loading-info').style.display='none';
          var string = '<a href="https://www.youtube.com/watch?v=' + id + '">' + 
                       '<img src="../images/play.jpg"/></a>';
          $('#play').html(string);
        });
        return false;      
      }
    )

    $('.link').hover(
      function() {
        $(this).css('opacity', '0.9');
      },
      function () {
        $(this).css('opacity', '1');
      }
    );

    $('.link').click( function () {
      var url = $(this).attr('href');
      console.log(url)
      window.open(url, '_blank');
    });


  })


  $(function(){
      $(window).resize(function(){
          var rankHeight = $('.rank').height();
          var scoreHeight = rankHeight/2;
          $('.score').css('height',scoreHeight + 'px');
      }).resize();    
  });
}

// ----------------- Event handlers -----------------


$(function() {
  $('#query_form').bind('submit', function() {
      console.log($('input[name="input"]').val());
      document.getElementById('loading').style.display='block';
      $.getJSON('./find_videos', {
        query: $('input[name="input"]').val(),
      }, function(data) {
        document.getElementById('loading').style.display='none';
        console.log(data.result);
        render_results(data.scores, data.thumbnails, data.descriptions, data.titles, data.urls);
      });
      return false;
  });
});

// ------------------------ Styling ------------------------

$(function() {
  $('#splashform').bind('submit', function() {
      console.log($('input[name="splash-input"]').val());
      document.getElementById('nav').style.display='none';
      document.getElementById('preloader').style.display='block';
      $.getJSON('./find_videos', {
        query: $('input[name="splash-input"]').val(),
      }, function(data) {
        console.log(data.result);
        document.getElementById('splashpage').style.display='none';
        document.getElementById('nav').style.display='block';
        render_results(data.scores, data.thumbnails, data.descriptions, data.titles, data.urls);
      });
      return false;
  });
});


$(function(){
    $(window).resize(function(){
        var rankHeight = $('.rank').height();
        var scoreHeight = rankHeight/2;
        $('.score').css('height',scoreHeight + 'px');
    }).resize();    
});

function show(shown, hidden) {
    document.getElementById(shown).style.display='block';
    document.getElementById(hidden).style.display='none';
    return false;
}

$(window).load(function() {
  document.getElementById('splashpage').style.display='block';
  document.getElementById('nav').style.display='none';
});