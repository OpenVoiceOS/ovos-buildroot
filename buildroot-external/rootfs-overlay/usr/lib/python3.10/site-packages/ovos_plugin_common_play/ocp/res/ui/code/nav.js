document.onkeydown = function(e) {
    switch (e.keyCode) {
        case 37:
            console.log('leftPageRequested');
            break;
        case 39:
            console.log('rightPageRequested');
            break;
    }
};

function useFullscreen() {
    var video = document.querySelector('video'); 
    var controlBar = findControlBar();

    while (document.body.firstChild) { 
      document.body.removeChild(document.body.firstChild);
     }; 
     document.body.appendChild(video);
     document.body.appendChild(controlBar);
     document.body.style.overflow = 'hidden';
     changeBackground();
     video.style.background = "black";
     video.play();
     hideScrollbar();
}

// Find element which contains control-bar
function findControlBar() {
    var allElements = document.querySelectorAll('*');
    for (var i = 0; i < allElements.length; i++) {
        if (allElements[i].className.indexOf('control-bar') != -1) {
            return allElements[i];
        }
    }
}

function hideScrollbar() {
    var style = document.createElement("style");
    style.innerHTML = `body::-webkit-scrollbar {display: none;}`;
    document.head.appendChild(style);
}

function changeBackground() {
    document.body.style.background = "black";
 }
