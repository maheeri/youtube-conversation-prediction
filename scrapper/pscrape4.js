/*
Input a json list of video ids as sys_arg and this will write scraped data to an
output folder /scraped/.
The scrape will contain the view data over time as well as the date the scrape
was run on.
A python script later extracts the exact date needed
*/


//Filereader and system
var fs = require('fs');
var system = require('system');

//Try to read json (sys arg)
try {
    file    = fs.open(system.args[1], "r");
    content = file.read();
    file.close();
} catch (e) {
    console.log(e);
}


var vidIDList           = JSON.parse(content);
var my_vidListIterator  = vidListIterator(vidIDList)

var recur_scrape = function(){
    if (my_vidListIterator.hasNext){
        vidID = my_vidListIterator.next();
        console.log(vidID);
        scrape(vidID, recur_scrape);
    }else{
        phantom.exit();
    }
}

recur_scrape();
   

function vidListIterator(vidIDList){
    return {
        vidIDList   : vidIDList,
        remaining   : vidIDList.length,
        hasNext     : function(){
                        return (this.remaining >= 1);
                    },
        next        : function(){
                        if (this.hasNext()){
                            this.remaining -= 1;
                            return this.vidIDList[this.remaining];
                        }else{
                            return false;
                        }

                    }
    }
}


//waitfor
/**
 * Wait until the test condition is true or a timeout occurs. Useful for waiting
 * on a server response or for a ui change (fadeIn, etc.) to occur.
 *
 * @param testFx javascript condition that evaluates to a boolean,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param onReady what to do when testFx condition is fulfilled,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param timeOutMillis the max amount of time to wait. If not specified, 3 sec is used.
 */
function waitFor(testFx, onReady, timeOutMillis) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 11000, //< Default Max Timout is 11s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    console.log("'waitFor()' timeout");
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    console.log("'waitFor()' finished in " + (new Date().getTime() - start) + "ms.");
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 250); //< repeat check every 250ms
};


/*
 The main scraping function
*/
function scrape(vidID, callback){
    var pageUrl = "http://youtube.com/watch?v="+vidID;
    //Page and System Creation
    var page = require("webpage").create();
    //Listeners//
    page.onConsoleMessage = function(msg) {
        console.log(msg);
    };
    //Open Page
    page.open(pageUrl, function (status) {
        if (status !== "success" && !page.injectJs('jquery-1.11.2.js')) {
            console.log("Unable to access network");
        } else {
            // Wait for clicking ability
            waitFor(function() {
                // Check in the element is defined
                return page.evaluate(function() {
                    return (document.getElementById("action-panel-overflow-button") != undefined);
                });
            }, function() {
                console.log("The page is now actually loaded");
                console.log("Trying to click 1st.");
                page.evaluate(function() {
                    document.getElementById("action-panel-overflow-button").click();
                })
                waitFor(function() {
                    // Check in the element is defined
                    return page.evaluate(function() {
                        return (document.getElementById("aria-menu-id-3") != undefined);
                    });
                }, function() {
                    console.log("The 1st button click worked.");
                    console.log("Trying to click 2nd.");
                    page.evaluate(function() {
                        /* Modfied: http://stackoverflow.com/questions/13765031/scrape-eavesdrop-ajax-data-using-javascript */
                        (function() {
                            var XHR = XMLHttpRequest.prototype;
                            // Remember references to original methods
                            var open = XHR.open;
                            var send = XHR.send;
                            // Overwrite native methods
                            // Collect data: 
                            XHR.open = function(method, url) {
                                this._method = method;
                                this._url = url;
                                return open.apply(this, arguments);
                            };
                            // Implement "ajaxSuccess" functionality
                            XHR.send = function(postData) {
                                this.addEventListener('load', function() {
                                    if (this._url.indexOf("insight_ajax?action_get_statistics_and_data")>-1){
                                        if (this.responseText == undefined){
                                            console.log("Something weird (responseText)");
                                        }else{
                                            window.viewTimeData = this.responseText;
                                        }
                                    }
                                });
                                return send.apply(this, arguments);
                            };
                        document.querySelector("button[data-trigger-for='action-panel-stats']").click();
                        })();
                    })
                    waitFor(function() {
                        // Check in the graph is loaded
                        return page.evaluate(function() {
                            return (document.querySelector("svg[aria-label='A chart.']") != undefined);
                        });
                    }, function() {
                        console.log("Graph is now displaying");
                        var scraped_data = page.evaluate(function(){
                            return window.viewTimeData;
                        })
                        //Get current time of scrape
                        var currentdate = new Date();
                        timeStr = '%TIME_START%'+currentdate.toDateString()+'%TIME_END% ';
                        scraped_data = timeStr+scraped_data;
                        //Write scrape to file
                        var path = 'scraped/';
                        fs.write(path+vidID+'.scrape', scraped_data, 'w');
                        page.close();
                        callback();
                    });
                });
            });
        }
    });
}