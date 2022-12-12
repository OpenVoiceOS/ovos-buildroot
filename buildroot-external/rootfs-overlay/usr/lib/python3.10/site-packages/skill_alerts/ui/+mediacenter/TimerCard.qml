import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import QtQuick.Window 2.12
import QtQuick.Shapes 1.12
import org.kde.kirigami 2.11 as Kirigami
import Mycroft 1.0 as Mycroft

ItemDelegate {
    id: timerCard
    implicitHeight: timerViews.height
    implicitWidth: timerViews.count == 1 ? timerViews.width : timerViews.width / 2.5
    property color backgroundColor: Kirigami.Theme.backgroundColor
    property color backgroundBorderColor: Qt.darker(Kirigami.Theme.backgroundColor, 1.2)
    property color primaryColor: Kirigami.Theme.highlightColor
    property color secondaryColor: Qt.lighter(Kirigami.Theme.highlightColor, 1.25)
    property color expiredColor: Kirigami.Theme.textColor
    property bool horizontalMode: width > height ? 1 : 0

    Component.onCompleted: {
        timerViewLayout.children[currentIndex].forceActiveFocus()
    }

    Keys.onReturnPressed: {
        if (timerViews.count == 1) {
            Mycroft.MycroftController.sendText("cancel all timers")
        }
        triggerGuiEvent("timerskill.gui.stop.timer", {"timer": modelData})
    }

    background: Rectangle {
        color: timerCard.backgroundColor
        border.color: timerCard.backgroundBorderColor
        border.width: 1
        radius: 15
    }

    contentItem: Item {

        Item {
            id: topArea
            width: parent.width
            height: parent.height * 0.15
            anchors.top: parent.top

            Label {
               color: timerCard.expiredColor
               fontSizeMode: Text.Fit
               minimumPixelSize: 5
               font.pixelSize: 72
               anchors.fill: parent
               anchors.margins: 10
               verticalAlignment: Text.AlignVCenter
               horizontalAlignment: Text.AlignHCenter
               text: modelData.timerName
            }
        }

        Item {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: topArea.bottom
            anchors.bottom: timerCard.activeFocus ? bottomArea.top : parent.bottom
            anchors.bottomMargin: parent.height * 0.10
            anchors.topMargin: parent.height * 0.10

            Rectangle {
                id: dialArea
                width: horizontalMode ? parent.width * 0.30 : parent.height * 0.95
                height: horizontalMode ? parent.width * 0.30 : parent.height * 0.95
                anchors.centerIn: parent

                color: "transparent"

                RoundProgress {
                    id: dddial
                    anchors.centerIn: parent
                    width: parent.width
                    height: parent.height
                    text: modelData.timeDelta
                    value: parseFloat(modelData.percentRemaining).toFixed(2);
                }
            }
        }

        Item {
            id: bottomArea
            width: parent.width
            height: parent.height * 0.15
            anchors.bottom: parent.bottom
            visible: timerCard.activeFocus ? 1 : 0
            enabled: timerCard.activeFocus ? 1 : 0

            Kirigami.Separator {
                id: sept
                anchors.top: parent.top
                width: parent.width
                color: timerCard.secondaryColor
                height: 1
            }

            Label {
                anchors.top: sept.bottom
                anchors.bottom: parent.bottom
                width: parent.width
                fontSizeMode: Text.Fit
                minimumPixelSize: 5
                font.pixelSize: 40
                maximumLineCount: 1
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                color: timerCard.expiredColor
                text: qsTr("Press Select To Cancel")
            }
        }
    }
}
