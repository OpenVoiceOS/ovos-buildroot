import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Window 2.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import QtMultimedia 5.12
import "." as Local

Item {
    id: nowPlayingHomeBar
    readonly property var mediaService: Mycroft.MediaService
    property var mediaStatus: mediaService.playbackState
    property var mediaTitle: sessionData.title
    property var mediaArtist: sessionData.artist
    property var mediaArt: sessionData.image

    Rectangle {
        anchors.fill: parent
        color: Kirigami.Theme.backgroundColor
        opacity: 0.95

        RowLayout {
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit
            spacing: Mycroft.Units.gridUnit

            Image {
                id: nowPlayingImage
                source: nowPlayingHomeBar.mediaArt
                Layout.fillHeight: true
                Layout.preferredWidth: nowPlayingImage.height
                fillMode: Image.PreserveAspectFit
                smooth: true
            }

            Controls.Label {
                id: nowPlayingLabel
                text: "Now Playing:"
                color: Kirigami.Theme.textColor
                Layout.fillHeight: true
                elide: Text.ElideRight
            }

            Controls.Label {
                id: nowPlayingTitle
                text: nowPlayingHomeBar.mediaTitle + " - " + nowPlayingHomeBar.mediaArtist
                color: Kirigami.Theme.textColor
                Layout.fillWidth: true                  
                Layout.fillHeight: true
                elide: Text.ElideRight
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            root.movePageRight()
        }
    }
}