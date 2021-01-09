import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

Mycroft.Delegate {
    id: mainLoaderView

    property var pageType: sessionData.page_type
    leftPadding: 0
    rightPadding: 0
    bottomPadding: 0
    topPadding: 0
    
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        
        ColumnLayout {
            id: grid
            anchors.fill: parent
            anchors.margins: Kirigami.Units.largeSpacing
            
            Label {
                id: statusLabel
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: parent.height * 0.075
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                font.family: "Noto Sans Display"
                font.styleName: "Black"
                text: "Starting Up"
                color: "white"
            }
            
            Label {
                id: statusLabel2
                Layout.alignment: Qt.AlignHCenter
                font.pixelSize: parent.height * 0.075
                wrapMode: Text.WordWrap
                renderType: Text.NativeRendering
                font.family: "Noto Sans Display"
                font.styleName: "Black"
                text: "Loading..."
                color: "#ff0000"
            }

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
                source: Qt.resolvedUrl("animations/installing.json")
            }
        }
    } 
}
