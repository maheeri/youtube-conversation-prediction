var phantom = require('phantom');
phantom.create(function(ph) {
  return ph.createPage(function(page) {
    return page.open("https://www.youtube.com/watch?v=0ne7ChIFlZg", function(status) {
      console.log("opened site? ", status);         
 
            page.includeJs('https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js', function() {
                //jQuery Loaded.
                //Wait for a bit for AJAX content to load on the page. Here, we are waiting 5 seconds.
                setTimeout(function() {
                    return page.evaluate(function() {
                        $jq = window.jQuery;
                        $jq.noConflict();
                        //Getting stats elements from youtube page
                        $jq("#action-panel-overflow-button").click();
                        $jq("button[data-trigger-for='action-panel-stats']").click();
                        return $jq("svg[aria-label='A chart.'] g").length; //this should be >0
                        var $graph  = $jq("svg[aria-label='A chart.'] g");
                        var rect   = $jq("svg[aria-label='A chart.'] g rect");
                        var height  = rect.attr('height');
                        var width   = rect.attr('width');
                        
                    }, function(result) {
                        console.log(result);
                        ph.exit();
                    });
                }, 2000);
 
            });
    });
    });
});