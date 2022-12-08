import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Control {
    id: boxoverlayroot
    Kirigami.Theme.inherit: false
    Kirigami.Theme.colorSet: Kirigami.Theme.View
    property bool horizontalMode: boxoverlayroot.width > boxoverlayroot.height ? 1 : 0

    background: Rectangle {
        width: idleRoot.width
        height: idleRoot.height
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: -Mycroft.Units.gridUnit * 2
        anchors.topMargin: -Mycroft.Units.gridUnit * 2
        color: Kirigami.Theme.backgroundColor
    }

    contentItem: Item {

        Kirigami.Heading {
            id: boxesOverlayHeader
            level: 1
            text: qsTr("Quick Access")
            color: Kirigami.Theme.textColor
            anchors.top: parent.top
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: boxesOverlayAddButton.right
            anchors.rightMargin: Mycroft.Units.gridUnit
            anchors.leftMargin: Mycroft.Units.gridUnit
        }

        Control {
            id: boxesOverlayAddButton
            anchors.top: parent.top
            anchors.topMargin: Mycroft.Units.gridUnit / 4
            anchors.bottom: boxesOverlayHeaderSept.top
            anchors.bottomMargin: Mycroft.Units.gridUnit / 4
            anchors.right: parent.right
            anchors.rightMargin: Mycroft.Units.gridUnit
            width: Mycroft.Units.gridUnit * 4

            background: Rectangle {
                id: boxesOverlayAddButtonBackground
                color: Kirigami.Theme.highlightColor
                radius: 6
            }

            contentItem: Kirigami.Icon {
                id: boxesOverlayAddButtonIcon
                source: "list-add-symbolic"
                color: Kirigami.Theme.textColor
                anchors.centerIn: parent
            }

            SequentialAnimation {
                id: boxesOverlayAddButtonAnimation
                PropertyAnimation { target: boxesOverlayAddButtonBackground; property: "color"; to: Kirigami.Theme.backgroundColor; duration: 200 }
                PropertyAnimation { target: boxesOverlayAddButtonBackground; property: "color"; to: Kirigami.Theme.highlightColor; duration: 200 }
            }

            MouseArea {
                anchors.fill: parent

                onClicked: {
                    boxesOverlayAddButtonAnimation.start()
                    Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
                    addCardOverlay.open()
                }
            }
        }

        Kirigami.Separator {
            id: boxesOverlayHeaderSept
            anchors.top: boxesOverlayHeader.bottom
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            height: 1
        }

        GridBox {
            id: gridBox
            visible: addCardOverlay.opened ? 0 : 1
            anchors.left: parent.left
            anchors.leftMargin: Mycroft.Units.gridUnit / 2
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: boxesOverlayHeaderSept.bottom
            anchors.topMargin: Mycroft.Units.gridUnit / 2
            anchors.bottom: boxesOverlayFooterSept.top
            anchors.bottomMargin: Mycroft.Units.gridUnit / 2
        }

        Kirigami.Separator {
            id: boxesOverlayFooterSept
            anchors.bottom: boxesOverlayFooter.top
            anchors.bottomMargin: Mycroft.Units.gridUnit / 2
            anchors.left: parent.left
            anchors.right: parent.right
            color: Kirigami.Theme.highlightColor
            height: 1
        }

        RowLayout {
            id: boxesOverlayFooter
            anchors.left: parent.left
            anchors.leftMargin: Mycroft.Units.gridUnit / 2
            anchors.right: parent.right
            anchors.rightMargin: Mycroft.Units.gridUnit / 2
            anchors.bottom: parent.bottom
            height: Mycroft.Units.gridUnit * 2

            Kirigami.Icon {
                id: boxesOverlayFooterIcon
                source: "documentinfo"
                color: Kirigami.Theme.highlightColor
                Layout.topMargin: Mycroft.Units.gridUnit / 3
                Layout.bottomMargin: Mycroft.Units.gridUnit / 3
                Layout.fillHeight: true
                Layout.preferredWidth: height
            }

            Label {
                id: boxesOverlayFooterLabel
                text: qsTr("Double-tap card to perform card action")
                color: Kirigami.Theme.textColor
                Layout.fillWidth: true
                Layout.fillHeight: true
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignLeft
                maximumLineCount: 1
                font.pixelSize: parent.height * 0.35
                fontSizeMode: Text.Fit
                minimumPixelSize: 8
                elide: Text.ElideRight
            }
        }

        AddCardOverlay {
            id: addCardOverlay
            width: parent.width
            height: parent.height
        }
    }
}

