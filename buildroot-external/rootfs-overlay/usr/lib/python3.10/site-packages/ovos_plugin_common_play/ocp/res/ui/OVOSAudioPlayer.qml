import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft
import QtQuick.Layouts 1.12
import QtGraphicalEffects 1.0
import QtQuick.Templates 2.12 as T
import QtMultimedia 5.12
import "code/helper.js" as HelperJS

Item {
    id: root
    readonly property var audioService: Mycroft.MediaService

    property var source
    property string status: "stop"
    property var thumbnail: sessionData.image
    property var title: sessionData.title
    property var author: sessionData.artist

    property var loopStatus: sessionData.loopStatus
    property var canResume: sessionData.canResume
    property var canNext: sessionData.canNext
    property var canPrev: sessionData.canPrev
    property var canRepeat: sessionData.canRepeat
    property var canShuffle: sessionData.canShuffle
    property var shuffleStatus: sessionData.shuffleStatus

    property var playerMeta
    property var cpsMeta

    //Player Support Vertical / Horizontal Layouts
    property bool horizontalMode: width > height ? 1 : 0

    //Player Button Control Actions
    property var currentState: audioService.playbackState

    //Mediaplayer Related Properties To Be Set By Probe MediaPlayer
    property var playerDuration
    property var playerPosition

    //Spectrum Related Properties
    property var spectrum: [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    property var soundModelLength: audioService.spectrum.length
    property color spectrumColorNormal: Kirigami.Theme.highlightColor
    property color spectrumColorMid: Kirigami.Theme.highlightColor
    property color spectrumColorPeak: Kirigami.Theme.textColor
    property real spectrumScale: 2.75
    property bool spectrumVisible: true
    property int spectrumType: sessionData.visualizationType ? sessionData.visualizationType : 1 // 1. Bars, 2. Waves
    readonly property real spectrumHeight: (rep.parent.height / normalize(spectrumScale))

    onSourceChanged: {
        console.log(source)
        play()
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

    function normalize(e){
        switch(e){case.1:return 10;case.2:return 9;case.3:return 8; case.4:return 7;case.5:return 6;case.6:return 5;case.7:return 4;case.8:return 3; case.9:return 2;case 1:return 1; default: return 1}
    }

    function play(){
        audioService.playURL(source)
    }

    function pause(){
        audioService.playerPause()
    }

    function stop(){
        audioService.playerStop()
    }

    function resume(){
        audioService.playerContinue()
    }

    function next(){
        audioService.playerNext()
    }

    function previous(){
        audioService.playerPrevious()
    }

    function repeat(){
        audioService.playerRepeat()
    }

    function shuffle(){
        audioService.playerShuffle()
    }

    function seek(val){
        audioService.playerSeek(val)
    }

    function restart(){
        audioService.playerRestart()
    }

    Connections {
        target: Mycroft.MediaService

        onDurationChanged: {
            playerDuration = dur
        }
        onPositionChanged: {
            playerPosition = pos
        }
        onPlayRequested: {
            source = audioService.getTrack()
        }

        onStopRequested: {
            source = ""
        }

        onMediaStatusChanged: {
            triggerGuiEvent("media.state", {"state": status})
            if (status == MediaPlayer.EndOfMedia) {
                pause()
            }
        }

        onMetaUpdated: {
            root.playerMeta = audioService.getPlayerMeta()

            if(root.playerMeta.hasOwnProperty("Title")) {
                root.title = root.playerMeta.Title ? root.playerMeta.Title : ""
            }

            if(root.playerMeta.hasOwnProperty("Artist")) {
                root.author = root.playerMeta.Artist
            } else if(root.playerMeta.hasOwnProperty("ContributingArtist")) {
                root.author = root.playerMeta.ContributingArtist
            }
            console.log("From QML Meta Updated Loading Metainfo")
            console.log("Author: " + root.author + " Title: " + root.title)
        }

        onMetaReceived: {
            root.cpsMeta = audioService.getCPSMeta()
            root.thumbnail = root.cpsMeta.thumbnail
            root.author = root.cpsMeta.artist
            root.title = root.cpsMeta.title

            console.log("From QML Media Received Loading Metainfo")
            console.log(JSON.stringify(root.cpsMeta))
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
            anchors.bottom: bottomBoxAboveInner.top
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
            id: bottomBoxAboveInner
            anchors.bottom: sliderBar.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: parent.height * 0.30
            color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 0.5)

            RowLayout {
                anchors.top: parent.top
                anchors.topMargin: Mycroft.Units.gridUnit
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: Mycroft.Units.gridUnit * 2
                anchors.rightMargin: Mycroft.Units.gridUnit * 2
                height: parent.height
                z: 2

                Label {
                    id: playerPosLabelBottom
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignLeft | Qt.AlignBottom
                    font.pixelSize: horizontalMode ? height * 0.35 : width * 0.10
                    horizontalAlignment: Text.AlignLeft
                    verticalAlignment: Text.AlignVCenter
                    text: playerPosition ? formatedPosition(playerPosition) : ""
                    color: Kirigami.Theme.textColor
                }

                Label {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.alignment: Qt.AlignRight | Qt.AlignBottom
                    font.pixelSize: horizontalMode ? height * 0.35 : width * 0.10
                    horizontalAlignment: Text.AlignRight
                    verticalAlignment: Text.AlignVCenter
                    text: playerDuration ? formatedDuration(playerDuration) : ""
                    color: Kirigami.Theme.textColor
                }
            }

            Item {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.bottomMargin: Mycroft.Units.gridUnit * 0.5
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.largeSpacing

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if(root.spectrumType == 1) {
                            root.spectrumType = 2
                            Mycroft.MycroftController.sendRequest("ovos.common_play.spectrum", {"type": 2})
                        } else {
                            root.spectrumType = 1
                            Mycroft.MycroftController.sendRequest("ovos.common_play.spectrum", {"type": 1})
                        }
                    }
                }

                Row {
                    id: visualizationRowItemParent
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: horizontalMode ? parent.width * 0.18 : parent.width * 0.14
                    anchors.rightMargin: horizontalMode ? parent.width * 0.18 : parent.width * 0.14
                    height: parent.height
                    spacing: 4
                    visible: spectrumVisible && spectrumType == 1
                    enabled: spectrumVisible && spectrumType == 1

                    Repeater {
                        id: rep
                        model: root.soundModelLength - 1

                        delegate: Rectangle {
                            width: (visualizationRowItemParent.width * 0.85) / root.soundModelLength
                            radius: 3
                            opacity: root.currentState === MediaPlayer.PlayingState ? 1 : 0
                            height: 15 + root.spectrum[modelData] * root.spectrumHeight
                            anchors.bottom: parent.bottom

                            gradient: Gradient {
                                GradientStop {position: 0.05; color: height > root.spectrumHeight / 1.25 ? spectrumColorPeak : spectrumColorNormal}
                                GradientStop {position: 0.25; color: spectrumColorMid}
                                GradientStop {position: 0.50; color: spectrumColorNormal}
                                GradientStop {position: 0.85; color: spectrumColorMid}
                            }

                            Behavior on height {
                                NumberAnimation {
                                    duration: 150
                                    easing.type: Easing.Linear
                                }
                            }
                            Behavior on opacity {
                                NumberAnimation{
                                    duration: 1500 + root.spectrum[modelData] * parent.height
                                    easing.type: Easing.Linear
                                }
                            }
                        }
                    }
                }

                SpectrumWaveDelegate {
                    height: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    visible: spectrumVisible && spectrumType == 2
                    enabled: spectrumVisible && spectrumType == 2
                    spectrumLocalLength: root.soundModelLength
                    spectrumLocalData: root.spectrum
                }
            }
        }


        T.Slider {
            id: sliderBar
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: innerBox.top
            height: Mycroft.Units.gridUnit
            to: playerDuration
            value: playerPosition
            z: 10

            onPressedChanged: {
                root.seek(value)

                if(pressed) {
                    hand.color = Kirigami.Theme.highlightColor
                    hand.border.color = Kirigami.Theme.backgroundColor
                } else {
                    hand.color = Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 1)
                    hand.border.color = Kirigami.Theme.highlightColor
                }
            }

            handle: Item {
                x: sliderBar.visualPosition * (parent.width - (Kirigami.Units.largeSpacing + Kirigami.Units.smallSpacing))
                anchors.verticalCenter: parent.verticalCenter
                height: parent.height + Mycroft.Units.gridUnit

                Rectangle {
                    id: hand
                    anchors.verticalCenter: parent.verticalCenter
                    implicitWidth: Kirigami.Units.iconSizes.small + Kirigami.Units.smallSpacing
                    implicitHeight: parent.height
                    color: Qt.rgba(Kirigami.Theme.backgroundColor.r, Kirigami.Theme.backgroundColor.g, Kirigami.Theme.backgroundColor.b, 1)
                    border.color: Kirigami.Theme.highlightColor
                }
            }


            background: Rectangle {
                color: Qt.lighter(Kirigami.Theme.highlightColor, 1.5)

                Rectangle {
                    width: sliderBar.visualPosition * parent.width
                    height: parent.height
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: Kirigami.Theme.highlightColor }
                        GradientStop { position: 1.0; color: Qt.darker(Kirigami.Theme.highlightColor, 1.5) }
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
                        repeat()
                    }

                    onPressed: {
                        repeatButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: root.loopStatus === "RepeatTrack" ? Qt.resolvedUrl("images/media-playlist-repeat-track.svg") : Qt.resolvedUrl("images/media-playlist-repeat.svg")

                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.loopStatus === "None" ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.3) : Kirigami.Theme.highlightColor
                        }
                    }

                    background: Rectangle {
                        id: repeatButtonBackground
                        radius: 5
                        color:  HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                    }
                }

                Button {
                    id: prevButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.right: playButton.left
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

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
                        previous()
                    }

                    onPressed: {
                        prevButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit

                        source: Qt.resolvedUrl("images/media-skip-backward.svg")

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
                    }
                }

                Button {
                    id: playButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

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
                        root.currentState === MediaPlayer.PlayingState ? root.pause() : root.currentState === MediaPlayer.PausedState ? root.resume() : root.play()
                    }

                    onPressed: {
                        playButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: root.currentState === MediaPlayer.PlayingState ? Qt.resolvedUrl("images/media-playback-pause.svg") : Qt.resolvedUrl("images/media-playback-start.svg")

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
                    }
                }

                Button {
                    id: nextButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: playButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

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
                        next()
                    }

                    onPressed: {
                        nextButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("images/media-skip-forward.svg")

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
                    }
                }

                Button {
                    id: shuffleButton
                    width: Math.round(parent.width / 5) - Mycroft.Units.gridUnit
                    height: parent.height
                    anchors.left: nextButton.right
                    anchors.margins: Mycroft.Units.gridUnit * 0.5

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
                        shuffle()
                    }

                    onPressed: {
                        shuffleButtonAnim.running = true;
                    }

                    contentItem: Kirigami.Icon {
                        anchors.fill: parent
                        anchors.margins: Mycroft.Units.gridUnit
                        source: Qt.resolvedUrl("images/media-playlist-shuffle.svg")

                        ColorOverlay {
                            source: parent
                            anchors.fill: parent
                            color: root.shuffleStatus === false ? Qt.rgba(Kirigami.Theme.textColor.r, Kirigami.Theme.textColor.g, Kirigami.Theme.textColor.b, 0.3) : Kirigami.Theme.highlightColor
                        }
                    }

                    background: Rectangle {
                        id: shuffleButtonBackground
                        radius: 5
                        color: HelperJS.isLight(Kirigami.Theme.backgroundColor) ? Qt.lighter(Kirigami.Theme.backgroundColor, 1.5) : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
                    }
                }
            }
        }
    }
}
