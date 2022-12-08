import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.0
import QtQuick.Templates 2.12 as T
import QtMultimedia 5.12
import "./code/helper.js" as HelperJS

Item {
    id: root

    property var thumbnail: sessionData.image
    property var title: sessionData.title
    property var author: sessionData.artist
    property var playerState: sessionData.status

    property var loopStatus: sessionData.loopStatus
    property var canResume: sessionData.canResume
    property var canNext: sessionData.canNext
    property var canPrev: sessionData.canPrev
    property var canRepeat: sessionData.canRepeat
    property var canShuffle: sessionData.canShuffle
    property var shuffleStatus: sessionData.shuffleStatus

    //Player Support Vertical / Horizontal Layouts
    //property bool horizontalMode: width > height ? 1 : 0
    property bool horizontalMode: false

    function formatedDuration(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    function formatedPosition(millis){
        var minutes = Math.floor(millis / 60000);
        var seconds = ((millis % 60000) / 1000).toFixed(0);
        return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
    }

    onFocusChanged: {
        if (focus) {
            repeatButton.forceActiveFocus()   
        }
    }

    KeyNavigation.down: repeatButton

    Connections {
        target: Window.window
        onVisibleChanged: {
            if(playerState === "Playing") {
                triggerGuiEvent("pause", {})
            }
        }
    }

    Image {
        id: imgbackground
        anchors.fill: parent
        source: root.thumbnail
    }

    FastBlur {
        anchors.fill: imgbackground
        radius: 64
        source: imgbackground
    }

    Rectangle {
        color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.5)
        radius: 5
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2

        GridLayout {
            anchors.top: parent.top
            anchors.bottom: innerBox.top
            anchors.left: parent.left
            anchors.right: parent.right
            rows: horizontalMode ? 2 : 1
            columns: horizontalMode ? 2 : 1

            Rectangle {
                id: rct1
                Layout.preferredWidth: horizontalMode ? img.width : parent.width
                Layout.preferredHeight:  horizontalMode ? parent.height : parent.height * 0.75
                color: "transparent"

                Image {
                    id: img
                    property bool rounded: true
                    property bool adapt: true
                    source: root.thumbnail
                    width: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    height: width
                    z: 20

                    layer.enabled: rounded
                    layer.effect: OpacityMask {
                        maskSource: Item {
                            width: img.width
                            height: img.height
                            Rectangle {
                                anchors.centerIn: parent
                                width: img.adapt ? img.width : Math.min(img.width, img.height)
                                height: img.adapt ? img.height : width
                                radius: 5
                            }
                        }
                    }
                }
            }
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"

                ColumnLayout {
                    id: songTitleText
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.smallSpacing

                    Label {
                        id: authortitle
                        text: root.author
                        maximumLineCount: 1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        font.bold: true
                        font.pixelSize: Math.round(height * 0.45)
                        fontSizeMode: Text.Fit
                        minimumPixelSize: Math.round(height * 0.25)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        font.capitalization: Font.Capitalize
                        color: Kirigami.Theme.textColor
                        visible: true
                        enabled: true
                    }

                    Label {
                        id: songtitle
                        text: root.title
                        maximumLineCount: 1
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        font.pixelSize: Math.round(height * 0.45)
                        fontSizeMode: Text.Fit
                        minimumPixelSize: Math.round(height * 0.25)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                        font.capitalization: Font.Capitalize
                        color: Kirigami.Theme.textColor
                        visible: true
                        enabled: true
                    }
                }
            }
        }
        Rectangle {
            id: innerBox
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: horizontalMode ? parent.height * 0.25 : parent.height * 0.20
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.7)

            Item {
                id: gridBar
                anchors.fill: parent
                anchors.margins: Mycroft.Units.gridUnit
                z: 10

                Button {
                    id: repeatButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.right: prevButton.left
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.right: prevButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    Keys.onLeftPressed: {
                        mainLoaderView.movePageLeft()
                    }

                    SequentialAnimation {
                        id: repeatButtonAnim
                        PropertyAnimation {
                            target: repeatButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                        PropertyAnimation {
                            target: repeatButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                    }

                    onClicked: {
                        repeatButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: root.loopStatus === "RepeatTrack" ? Qt.resolvedUrl("../images/media-playlist-repeat.svg") : root.loopStatus === "None" ? Qt.resolvedUrl("../images/media-playlist-repeat-track.svg") : Qt.resolvedUrl("images/media-playlist-repeat.svg")
                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.loopStatus === "None" ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4) : Kirigami.Theme.textColor
                        }
                    }

                    background: Rectangle {
                        id: repeatButtonBackground
                        radius: 5
                        color:  HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: repeatButton.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                        border.width: repeatButton.activeFocus ? 2 : 0
                    }
                }

                Button {
                    id: prevButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.right: playButton.left
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: repeatButton
                    KeyNavigation.right: playButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    SequentialAnimation {
                        id: prevButtonAnim
                        PropertyAnimation {
                            target: prevButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                        PropertyAnimation {
                            target: prevButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                    }

                    onClicked: {
                        prevButtonAnim.running = true;
                        triggerGuiEvent("previous", {})
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit

                        source: Qt.resolvedUrl("../images/media-skip-backward.svg")
                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.canPrev === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                        }
                    }

                    background: Rectangle {
                        id: prevButtonBackground
                        radius: 5
                        color:  HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: prevButton.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                        border.width: prevButton.activeFocus ? 2 : 0
                    }
                }

                Button {
                    id: playButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: prevButton
                    KeyNavigation.right: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    SequentialAnimation {
                        id: playButtonAnim

                        PropertyAnimation {
                            target: playButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                        PropertyAnimation {
                            target: playButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                    }

                    onClicked: {
                        playButtonAnim.running = true;
                        if (playerState === "Paused"){
                            playerState = "Playing"
                            triggerGuiEvent("resume", {})
                        } else {
                            playerState = "Paused"
                            triggerGuiEvent("pause", {})
                        }
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: playerState === MediaPlayer.PlayingState ? Qt.resolvedUrl("../images/media-playback-pause.svg") : Qt.resolvedUrl("../images/media-playback-start.svg")
                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.canResume === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                        }
                    }

                    background: Rectangle {
                        id: playButtonBackground
                        radius: 5
                        color: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: playButton.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                        border.width: playButton.activeFocus ? 2 : 0
                    }
                }

                Button {
                    id: nextButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: playButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: playButton
                    KeyNavigation.right: shuffleButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    SequentialAnimation {
                        id: nextButtonAnim
                        PropertyAnimation {
                            target: nextButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                        PropertyAnimation {
                            target: nextButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                    }

                    onClicked: {
                        nextButtonAnim.running = true;
                        triggerGuiEvent("next", {})
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("../images/media-skip-forward.svg")
                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.canNext === true ? Kirigami.Theme.textColor : Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4)
                        }
                    }

                    background: Rectangle {
                        id: nextButtonBackground
                        radius: 5
                        color: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: nextButton.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                        border.width: nextButton.activeFocus ? 2 : 0
                    }
                }

                Button {
                    id: shuffleButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: nextButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

                    KeyNavigation.left: nextButton
                    Keys.onReturnPressed: {
                         clicked()
                    }

                    Keys.onRightPressed: {
                        mainLoaderView.movePageRight()
                    }

                    SequentialAnimation {
                        id: shuffleButtonAnim
                        PropertyAnimation {
                            target: shuffleButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.darker(Kirigami.Theme.backgroundColor, 1.5) : Qt.lighter(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                        PropertyAnimation {
                            target: shuffleButtonBackground
                            property: "color"
                            to: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                            duration: 200
                        }
                    }

                    onClicked: {
                        shuffleButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("../images/media-playlist-shuffle.svg")
                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.shuffleStatus === false ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.4) : Kirigami.Theme.textColor
                        }
                    }

                    background: Rectangle {
                        id: shuffleButtonBackground
                        radius: 5
                        color: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                        border.color: shuffleButton.activeFocus ? Kirigami.Theme.highlightColor : "transparent"
                        border.width: shuffleButton.activeFocus ? 2 : 0
                    }
                }
            }
        }
    }
}

