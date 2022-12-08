import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import org.kde.kirigami 2.11 as Kirigami

Rectangle {
    id: alarmControl
    color: "transparent"
    border.color: Kirigami.Theme.highlightColor
    border.width: 4
    radius: 6
    property alias text: alarmTimeText.text
    property bool expired: false

    Text {
        id: alarmTimeText
        color: Kirigami.Theme.textColor
        fontSizeMode: Text.Fit
        minimumPixelSize: 5
        font.pixelSize: 72
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit / 2
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter

        SequentialAnimation on opacity {
            id: expireAnimation
            running: alarmControl.expired
            loops: Animation.Infinite
            PropertyAnimation {
                from: 1;
                to: 0;
                duration: 1000
            }
            PropertyAnimation {
                from: 0;
                to: 1;
                duration: 1000
            }
        }
    }
}