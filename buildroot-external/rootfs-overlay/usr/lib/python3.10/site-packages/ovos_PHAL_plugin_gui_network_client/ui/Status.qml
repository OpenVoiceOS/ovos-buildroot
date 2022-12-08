import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft

Rectangle {
    id: root
    anchors.fill: parent
    color: sessionData.color
    property bool horizontalMode: root.width > root.height ? 1 : 0
    
    ColumnLayout {
        id: grid
        anchors.fill: parent
            
        Image {
            id: statusIcon
            visible: true
            enabled: true
            Layout.preferredWidth: horizontalMode ? parent.width / 4 : parent.width / 2
            Layout.preferredHeight: width
            Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
            source: sessionData.image
        }

        Label {
            id: statusLabel
            Layout.alignment: Qt.AlignBottom | Qt.AlignHCenter
            Layout.bottomMargin: Kirigami.Units.largeSpacing
            font.pixelSize: parent.width * 0.075
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
