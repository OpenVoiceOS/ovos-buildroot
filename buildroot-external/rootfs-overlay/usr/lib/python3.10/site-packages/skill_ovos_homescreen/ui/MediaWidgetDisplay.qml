import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Layouts 1.4
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: mediaWidgetDisplayRoot
    color: Kirigami.Theme.backgroundColor
    border.color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
    border.width: 1
    radius: 8
    readonly property var audioService: Mycroft.MediaService
    property var spectrum: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    property var spectrumModelLength: audioService.spectrum.length
    property bool verticalMode: false
    layer.enabled: true
    layer.effect: DropShadow {
        horizontalOffset: 0
        verticalOffset: 0
        spread: 0.1
        radius: 10
        samples: 17
        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.5)
    }

    function calculateTextDistance(text, availableWidth) {
        var distance = text.length * 10 + (availableWidth * 2)
        return distance
    }

    Timer {
        id: sampler
        running: true
        interval: 100
        repeat: true
        onTriggered: {
            spectrum = audioService.spectrum
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 0.3

        MediaWidgetButton {
            buttonIcon: idleRoot.mediaWidgetState == "playing" ? "media-playback-pause" : "media-playback-start"
            onClicked: {
                if (idleRoot.mediaWidgetState == "playing") {
                    audioService.playerPause()
                 } else { 
                    audioService.playerContinue()
                 }
            }
        }
        
        MediaWidgetButton {
            buttonIcon: "media-playback-stop"
            onClicked: {
                audioService.playerStop()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: Mycroft.Units.gridUnit * 0.3
            radius: 8
            color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.1)
            clip: true

            Row {
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 4
                height: parent.height

                Repeater {
                    id: spectrumRepeater
                    model: spectrumModelLength - 1
                    delegate: Rectangle {
                        radius: 3
                        anchors.bottom: parent.bottom
                        visible: idleRoot.mediaWidgetState == "playing" ? 1 : 0
                        width: parent.width / (spectrumModelLength - 1)
                        height: 15 + mediaWidgetDisplayRoot.spectrum[modelData] * spectrumRepeater.parent.height * 0.5
                        color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.1)
                    }
                }
            }

            Mycroft.MarqueeText {
                id: titleText
                anchors.fill: parent
                anchors.leftMargin: Mycroft.Units.gridUnit * 0.2
                anchors.rightMargin: Mycroft.Units.gridUnit * 0.2
                text: idleRoot.mediaWidgetData.title + " - " + idleRoot.mediaWidgetData.artist
                color: Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.7)
                font.pixelSize: mediaWidgetDisplayRoot.verticalMode ? Mycroft.Units.gridUnit * 1 : Mycroft.Units.gridUnit * 2
                rightToLeft: true
                speed: 9000
                delay: 2000

                onTextChanged: {
                    titleText.distance = calculateTextDistance(titleText.text, titleText.width)
                    titleText.speed = 9000 + (titleText.distance * 0.5)
                }

                onDistanceChanged: {
                    // Reset the view
                    titleText.visible = false
                    titleText.enabled = false
                    titleText.visible = true
                    titleText.enabled = true
                }
            }
        }

        MediaWidgetButton {
            buttonIcon: "drag-surface"
            onClicked: {
                Mycroft.MycroftController.sendRequest("ovos.common_play.home", {})
            }
        }
    }
}