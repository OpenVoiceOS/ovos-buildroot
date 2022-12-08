import QtQuick.Layouts 1.4
import QtQuick 2.9
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: timeDisplay
    color: "transparent"
    property bool verticalMode: false
    property var time_string: sessionData.time_string ? sessionData.time_string.replace(":", "꞉") : ""

    Label {
        id: time
        width: parent.width
        height: parent.height
        font.capitalization: Font.AllUppercase
        horizontalAlignment: timeDisplay.verticalMode ? Text.AlignHCenter : (idleRoot.rtlMode ? Text.AlignRight : Text.AlignLeft)
        verticalAlignment: timeDisplay.verticalMode ? Text.AlignBottom : Text.AlignVCenter
        font.weight: Font.ExtraBold
        fontSizeMode: Text.Fit
        minimumPixelSize: timeDisplay.verticalMode ? parent.height / 2 : parent.height
        font.pixelSize: parent.height
        color: "white"
        text: timeDisplay.time_string
        layer.enabled: true
        layer.effect: DropShadow {
            verticalOffset: 4
            color: idleRoot.shadowColor
            radius: 11
            spread: 0.4
            samples: 16
        }
    }
}
