// ==UserScript==
// @name Test Automation for ACC
// @namespace https://control.akamai.com/apps/*
// @description Adds a button that when clicked, trigger the script for Test Automation
// @match https://control.akamai.com/apps/property-manager/*
// @require http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js
// @updateURL https://github.com/suhasAkamai/Test-Automation
// @downloadURL https://github.com/suhasAkamai/Test-Automation
// @version 2.1
// @grant none
// @run-at      document-idle
// ==/UserScript==

/*

1.0:
Initial version, creates a button within ACC to trigger Test Automation

*/


(function() {
    'use strict';
    console.log("Script executed")
    var stopTimer = 0;
    var doneButton = 0;
    var doneName = 0;
    var observer = new MutationObserver(resetTimer);
    var timer = setTimeout(setButton, 15000, observer); // wait for the page to stay still for 4 seconds
    observer.observe(document, { childList: true, subtree: true });

    function resetTimer(changes, observer) {
        console.log('resetTimer called');
        clearTimeout(timer);
        if (doneButton == 0 || doneName == 0){
            timer = setTimeout(setButton, 15000, observer);
        }
    }




 function doStartPMCoolness(configname,configversion,acc_name){
     console.log(configname)
     console.log(configversion)
     console.log('Inside the cool function');
     setTimeout(function () {
        var url = 'http://localhost:5000/parseconfig?config_name='+configname+'&config_version='+configversion+'&account_name='+acc_name;
        window.open(url);

    }, 500);



 }

 function setButton(){
 //var b = document.querySelector("body > akam-menu-header > akam-pulsar-header > section > div.pulsar-header__item--spacer")
   var b= document.querySelector("body > div > div > ui-view > akam-tabs > div > div > ui-view > div > div > div > div")
   var configname
   var configversion
   var res=""
 if (typeof b != 'undefined' && doneButton == 0) {
     console.log(b)
    console.log('spacer finally found');
    //stopTimer = 1;
     doneButton = 1;

    var node = document.createElement("button");
    node.textContent = 'Trigger ATC Tests';
    node.id = 'triggeratcid';
    node.class = 'pulsar-header__create-button ng-scope';
    b.append(node);

    var nam = document.getElementsByClassName('page-sub-title')[0].textContent;
    var acc_name_node=document.getElementsByClassName('pulsar-account-selector__account-name')
    var acc_name=acc_name_node[0].textContent


    console.log(nam)
    console.log(acc_name)
    if (typeof nam != 'undefined' && nam!= null && doneName == 0) {
        console.log('config name found');
        doneName = 1;
        res=nam.split(" ")
        console.log(res)
        console.log(res[0])
        console.log(res[1])
    }else{
        console.log('config name NOT found.. yet');
    }



    const button = document.getElementById("triggeratcid");
    button.addEventListener("click", event => {
        doStartPMCoolness(res[0],res[1],acc_name);
    });


 }else{
     console.log('spacer NOT found.. yet');
 }

}
})();
