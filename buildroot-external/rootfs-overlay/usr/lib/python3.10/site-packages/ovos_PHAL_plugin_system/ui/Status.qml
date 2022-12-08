import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0


Mycroft.Delegate {
    id: root
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0
    background: Rectangle {
        color: Kirigami.Theme.backgroundColor
        z: -1
    }
    property var success: sessionData.status
    anchors.fill: parent

    function checkstatus(status) {
        if(status == "Enabled") {
            return Qt.resolvedUrl("animations/status-success.json")
        } else if (status == "Disabled") {
            return Qt.resolvedUrl("animations/status-fail.json")
        }
    }
    
    Rectangle {
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2
        color: Kirigami.Theme.backgroundColor
        
        ColumnLayout {
            id: grid
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing

            LottieAnimation {
                id: statusIcon
                visible: true
                enabled: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.alignment: Qt.AlignHCenter
                loops: Animation.Infinite
                fillMode: Image.PreserveAspectFit
                running: true
                source: checkstatus(sessionData.status)
            }

            Label {
                id: statusLabel
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: parent.height * 0.095
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                font.family: "Noto Sans Display"
                font.styleName: "Black"
                text: sessionData.label
                color: Kirigami.Theme.textColor
            }
        }
    }
}
