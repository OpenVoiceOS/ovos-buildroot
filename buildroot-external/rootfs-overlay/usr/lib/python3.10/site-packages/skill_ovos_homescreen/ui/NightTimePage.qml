import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Control {
    id: nightTimeOverlayRoot
    Kirigami.Theme.inherit: false
    Kirigami.Theme.colorSet: Kirigami.Theme.View

    property bool horizontalMode: nightTimeOverlayRoot.width > nightTimeOverlayRoot.height ? 1 : 0
    property var time_string: sessionData.time_string ? sessionData.time_string.replace(":", "꞉") : ""

    background: Rectangle {
        width: idleRoot.width
        height: idleRoot.height
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: -Mycroft.Units.gridUnit * 2
        anchors.topMargin: -Mycroft.Units.gridUnit * 2
        color: "#000000"
    }

    contentItem: Item {

        Label {
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit * 4
            font.capitalization: Font.AllUppercase
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment:Text.AlignVCenter
            font.weight: Font.ExtraBold
            fontSizeMode: Text.Fit
            minimumPixelSize: 20
            font.pixelSize: parent.height
            color: "#cdcdcd"
            text: nightTimeOverlayRoot.time_string
        }
    }
}

