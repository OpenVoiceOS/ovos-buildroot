import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12 as Controls
import org.kde.kirigami 2.10 as Kirigami
import QtQuick.Window 2.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import QtMultimedia 5.12
import "." as Local

Mycroft.Delegate {
    id: root
    skillBackgroundSource: "https://source.unsplash.com/1920x1080/?+music"
    property bool compactMode: parent.height >= 550 ? 0 : 1
    property bool displayBottomBar: sessionData.displayBottomBar ? sessionData.displayBottomBar : 0
    fillWidth: true
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0
    readonly property var mediaService: Mycroft.MediaService
    property var mediaStatus: mediaService.playbackState

    function movePageRight(){
        parent.parent.parent.currentIndex++
        parent.parent.parent.currentItem.contentItem.forceActiveFocus()
    }

    Component.onCompleted: {
        if(root.visible) {
            if(homescreenStackLayout.currentIndex === 0){
                search.forceActiveFocus()
            }
            if(homescreenStackLayout.currentIndex === 1){
                ocpSkillsView.forceActiveFocus()
            }
        }
    }

    onGuiEvent: {
        switch (eventName) {
            case "ocp.gui.show.busy.overlay":
                busyPageOverlay.open = true
                break
            case "ocp.gui.hide.busy.overlay":
                busyPageOverlay.open = false
                break
        }
    }

    Rectangle {
        id: busyPageOverlay
        visible: busyPageOverlay.open ? 1 : 0
        enabled: busyPageOverlay.open ? 1 : 0
        z: 2
        property bool open: false
        anchors.fill: parent
        color: Kirigami.Theme.backgroundColor
        opacity: busyPageOverlay.open ? 0.95 : 0
        radius: 10
        property var indicatorText: sessionData.footer_text ? sessionData.footer_text : "Loading"
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 0
            radius: 10
            samples: 16
            color: Kirigami.Theme.backgroundColor
        }

        Behavior on opacity {
            NumberAnimation {
                duration: 200
            }
        }

        Controls.BusyIndicator {
            id: viewBusyIndicator
            visible: busyPageOverlay.visible
            anchors.centerIn: parent
            running: busyPageOverlay.visible
            enabled: busyPageOverlay.visible

            Controls.Label {
                id: viewBusyIndicatorLabel
                visible: busyPageOverlay.visible
                enabled: busyPageOverlay.visible
                anchors.top: parent.bottom
                color: Kirigami.Theme.textColor
                anchors.horizontalCenter: parent.horizontalCenter
                text: busyPageOverlay.indicatorText
            }
        }
    }

    StackLayout {
        id: homescreenStackLayout
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: displayBottomBar ? bottomBar.top : parent.bottom
        anchors.bottomMargin: displayBottomBar ? Mycroft.Units.gridUnit * 0.5 : 0
        anchors.margins: Mycroft.Units.gridUnit * 2
        clip: true
        currentIndex: sessionData.homepage_index ? sessionData.homepage_index : 0

        Search {
            id: search
            anchors.fill: parent
        }

        OCPSkillsView {
            id: ocpSkillsView
            anchors.fill: parent
        }
    }

    Rectangle {
        id: bottomBar
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: nowPlayingHomeBar.visible ? Mycroft.Units.gridUnit * 7 : Mycroft.Units.gridUnit * 4
        color: "transparent"
        visible: displayBottomBar
        enabled: displayBottomBar

        Kirigami.Separator {
            id: bottomBarSeparator
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
        }

        NowPlayingHomeBar {
            id: nowPlayingHomeBar
            anchors.top: bottomBarSeparator.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            height: Mycroft.Units.gridUnit * 3
            visible: root.mediaStatus === MediaPlayer.PlayingState ? 1 : 0
            enabled: root.mediaStatus === MediaPlayer.PlayingState ? 1 : 0
        }

        Kirigami.Separator {
            id: bottomBarSeparatorBarSept
            anchors.top: nowPlayingHomeBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            visible: nowPlayingHomeBar.visible
            enabled: nowPlayingHomeBar.enabled
        }

        GridLayout {
            id: bottomBarLayout
            anchors.top: nowPlayingHomeBar.visible ? bottomBarSeparatorBarSept.bottom : bottomBarSeparator.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: Mycroft.Units.gridUnit * 0.5
            columns: 2
            columnSpacing: Mycroft.Units.gridUnit * 0.5
            rowSpacing: Mycroft.Units.gridUnit * 0.5

            Rectangle {
                id: homepageButtonTangle
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Kirigami.Theme.backgroundColor
                border.color: homepageButtonTangle.activeFocus ? Kirigami.Theme.highlightColor : Kirigami.Theme.backgroundColor
                border.width: homepageButtonTangle.activeFocus ? 2 : 0
                radius: 6

                Keys.onRightPressed: {
                    skillsViewButtonTangle.forceActiveFocus()
                }

                Keys.onUpPressed: {
                    if(homescreenStackLayout.currentIndex === 0){
                        search.forceActiveFocus()
                    }
                    if(homescreenStackLayout.currentIndex === 1){
                        ocpSkillsView.forceActiveFocus()
                    }
                }

                Keys.onReturnPressed: {
                    homescreenStackLayout.currentIndex = 0
                }

                Controls.Label {
                    id: homepageButtonLabel
                    anchors.centerIn: parent
                    text: "Home"
                    font.pixelSize: parent.height * 0.5
                    color: homescreenStackLayout.currentIndex == 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        homescreenStackLayout.currentIndex = 0
                    }
                    onPressed: {
                        homepageButtonTangle.color = Kirigami.Theme.highlightColor
                        homepageButtonLabel.color = Kirigami.Theme.backgroundColor
                    }
                    onReleased: {
                        homepageButtonTangle.color = Kirigami.Theme.backgroundColor
                        homepageButtonLabel.color = homescreenStackLayout.currentIndex == 0 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    }
                }
            }

            Rectangle {
                id: skillsViewButtonTangle
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Kirigami.Theme.backgroundColor
                border.color: skillsViewButtonTangle.activeFocus ? Kirigami.Theme.highlightColor : Kirigami.Theme.backgroundColor
                border.width: skillsViewButtonTangle.activeFocus ? 2 : 0
                radius: 6

                Keys.onLeftPressed: {
                    homepageButtonTangle.forceActiveFocus()
                }
                
                Keys.onUpPressed: {
                    if(homescreenStackLayout.currentIndex === 0){
                        search.forceActiveFocus()
                    }
                    if(homescreenStackLayout.currentIndex === 1){
                        ocpSkillsView.forceActiveFocus()
                    }
                }

                Keys.onReturnPressed: {
                    homescreenStackLayout.currentIndex = 1
                }

                Controls.Label {
                    id: skillsViewButtonLabel
                    anchors.centerIn: parent
                    text: "Skills"
                    font.pixelSize: parent.height * 0.5
                    color: homescreenStackLayout.currentIndex == 1 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        homescreenStackLayout.currentIndex = 1
                    }
                    onPressed: {
                        skillsViewButtonTangle.color = Kirigami.Theme.highlightColor
                        skillsViewButtonLabel.color = Kirigami.Theme.backgroundColor
                    }
                    onReleased: {
                        skillsViewButtonTangle.color = Kirigami.Theme.backgroundColor
                        skillsViewButtonLabel.color = homescreenStackLayout.currentIndex == 1 ? Kirigami.Theme.highlightColor : Kirigami.Theme.textColor
                    }
                }
            }
        }
    }
}