  // ----------------- Global -----------------

$(function() {
  $main_container = $('.main_container');
  $input_panel = $('#input_panel');
  $input_form = $('#input_form');
  $query_input_field = $('#query_input_field');
  $error_text = $('.error_text');

  $info_panel = $('#info_panel');
  $results = $('#results')
  $map_canvas = $('#map-canvas');
  $spinner = $('#spinner');
  $result_count = $('#result_count');
  $display_input = $('#display_input');
  $back_button = $('#back_button');
  $results_button = $('#results_button');

  // ----------------- Event handlers -----------------

  $input_form.submit(function(event) {
    event.preventDefault();
    var input = $query_input_field.val();

    var error = '';
    if(!input) {
      error = 'No input query!';
    } else {
      console.log('Searching youtube...');
      find_videos(input, $results);
    }

    if(error) {
      $error_text.text(error).show().delay(2000).fadeOut(1000);
    }
  });

});

// ------------------------ Functions ------------------------

function find_videos(input, reuslt_pane) {
  $.ajax({
    type: 'POST',
    url: '/find_videos',
    data: {query: input},
  }).done(function(data) {
    console.log(data);
    $spinner.hide(500);
    if(data) {
      display_results(input, reuslt_pane); //fix
    } else {
      console.log('Invalid response');
    }
  }).fail(function(error, status) {
    alert(error.responseText + ' ' + status);
  });
}

function display_results(input, reuslt_pane) {
  var results = data['results']

  $results.html('');
  for(var video in results) {
    var vidID   = video[vid_id]
    var title   = video[vid_title]
    var realCom = video[vid_real_com]
    var predCom = video[vid_pred]


    var test_str = '<div class="result"> <b>'+title+'</b><br> <a href="https://www.youtube.com/watch?v="'+vidID+'">Link</a> <table> <tr> <td>Conversationality Score: </td> <td>&nbsp;</td> <td>'+predCom+'</td> </tr> <tr> <td>Real Score: </td> <td>&nbsp;</td> <td>'+realCom+'</td> </tr> </table> </div> <br>';
    var $entry = $('')
      .html(test_str);

    reuslt_pane.append($entry);
  }
}