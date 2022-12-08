import QtQuick.Layouts 1.12
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: mainLoaderView
    fillWidth: true
    skillBackgroundSource: sessionData.bg_image
    skillBackgroundColorOverlay: Qt.rgba(0, 0, 0, 0.85)
    leftPadding: 0
    topPadding: 0
    bottomPadding: 0
    rightPadding: 0
    property var backgroundAllowedPlayers: ["OVOSAudioPlayer.qml", "OVOSSyncPlayer.qml"]

    function movePageRight(){
        parent.parent.parent.currentIndex++
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }

    function movePageLeft(){
        parent.parent.parent.currentIndex--
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }

    onGuiEvent: {
        switch (eventName) {
            case "ocp.gui.player.loader.clear":
                rootLoader.source = ""
                break
        }
    }

    onFocusChanged: {
        if(focus) {
            rootLoader.item.forceActiveFocus()
        }
    }

    background: Rectangle {
        color: Kirigami.Theme.backgroundColor
        z: -1
    }

    property var pageToLoad: sessionData.playerBackend

    contentItem: Loader {
        id: rootLoader
    }

    onPageToLoadChanged: {
        console.log(sessionData.playerBackend)
        // Check if the page to load is in the backround allowed players list

        if (backgroundAllowedPlayers.indexOf(pageToLoad) !== -1) {
            mainLoaderView.skillBackgroundSource = sessionData.bg_image
        } else {
            mainLoaderView.skillBackgroundSource = null
        }

        // If the full url is: file:///home/mycroft/.local/share/mycroft/skills/ovos-skill-mpd-player/ui/Player.qml
        // insert a +mediacenter to get: file:///home/mycroft/.local/share/mycroft/skills/ovos-skill-mpd-player/ui/+mediacenter/Player.qml on sessionData.playerBackend
        var player_path = sessionData.playerBackend
        var mediacenter_player_path = player_path.replace("ui/", "ui/+mediacenter/")
        console.log("Loading player: " + mediacenter_player_path)
        rootLoader.setSource(mediacenter_player_path)
        rootLoader.item.forceActiveFocus()
    }
}