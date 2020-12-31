import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.ProportionalDelegate {
    id: root
    skillBackgroundColorOverlay: sessionData.bgColor
    
    ColumnLayout {
        id: grid
        anchors.centerIn: parent

        Image {
            id: statusIcon
            visible: true
            enabled: true
            anchors.horizontalCenter: grid.horizontalCenter
            Layout.preferredWidth: proportionalGridUnit * 50
            Layout.preferredHeight: proportionalGridUnit * 50
            source: Qt.resolvedUrl(`icons/${sessionData.icon}`)
        }

        /* Add some spacing between icon and text */
        Item {
            height: Kirigami.Units.largeSpacing
        }

        Label {
            id: statusLabel
            Layout.alignment: Qt.AlignHCenter
            font.pixelSize: 65
            wrapMode: Text.WordWrap
            renderType: Text.NativeRendering
            font.family: "Noto Sans Display"
            font.styleName: "Black"
            font.capitalization: Font.AllUppercase
            text: sessionData.label
            color: "white"
        }
    }
}