import QtQuick 2.4
import QtQuick.Controls 2.2
import QtWebEngine 1.8
import QtQuick.Layouts 1.4
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft


Item {
    id: root
    property var pageUrl: sessionData.uri
    
    onPageUrlChanged: {
        console.log("opening webview from mediacenter")
        console.log(pageUrl)
        webview.url = pageUrl
    }

    function viewLeftPressed() {
        parent.parent.parent.currentIndex--
    }

    function viewRightPressed() {
        parent.parent.parent.currentIndex++
    }

    WebEngineView {
        id: webview
        anchors.fill: parent
        settings.autoLoadImages: true
        settings.javascriptEnabled: true
        settings.errorPageEnabled: true
        settings.pluginsEnabled: true
        settings.allowWindowActivationFromJavaScript: true
        settings.javascriptCanOpenWindows: true
        settings.fullScreenSupportEnabled: true
        settings.autoLoadIconsForPage: true
        settings.touchIconsEnabled: true
        settings.webRTCPublicInterfacesOnly: true
        url: sessionData.uri

        onLoadingChanged: {
            if(loadRequest.status == WebEngineView.LoadSucceededStatus && sessionData.javascript){
                webview.runJavaScript(sessionData.javascript, function(result) { console.log(result); })
            }
        }

        userScripts: [
            WebEngineScript {
                injectionPoint: WebEngineScript.Deferred
                name: "NavJS"
                worldId: WebEngineScript.MainWorld
                sourceUrl: Qt.resolvedUrl("../code/nav.js")
            }
        ]

        onNewViewRequested: function(request) {
            if (!request.userInitiated) {
                console.log("Warning: Blocked a popup window.");
            } else {
                request.openIn(webview);
            }
        }
        
        onJavaScriptDialogRequested: function(request) {
            request.accepted = true;
        }

        onFullScreenRequested: {
            request.accept()
        }

        onJavaScriptConsoleMessage: {
            console.log(message)
            if(message == "rightPageRequested") {
                viewRightPressed()
            }
            if(message == "leftPageRequested") {
                viewLeftPressed()
            }
        }
    }
} 
