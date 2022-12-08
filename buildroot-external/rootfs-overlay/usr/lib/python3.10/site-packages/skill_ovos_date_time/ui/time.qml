import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import QtQuick.Window 2.3
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: timeRoot
    skillBackgroundColorOverlay: Qt.rgba(0, 0, 0, 1)
    leftPadding: 0
    rightPadding: 0
    bottomPadding: 0
    topPadding: 0
    
    property bool horizontalMode: timeRoot.width > timeRoot.height ? 1 : 0
    property var horizontalFontWidth: horizontalMode ? rectGrid.implicitWidth / 2 - colons.implicitWidth : rectGrid.implicitWidth / 2
    property var hourText: sessionData.time_string.split(":")[0]
    property var minuteText: sessionData.time_string.split(":")[1]
    
    onHourTextChanged: {
        hour.text = hourText
    }
    
    onMinuteTextChanged: {
        minute.text = minuteText
    }
    
    Item {
        anchors.fill: parent
        anchors.margins: horizontalMode ? timeRoot.height * 0.30 : timeRoot.height * 0.15
        
        Rectangle {
            id: rectGrid
            implicitWidth: parent.width
            implicitHeight: parent.height
            color: "transparent"

            GridLayout {
                id: gridtype
                height: parent.height
                anchors.centerIn: parent
                columns: horizontalMode ? 3 : 1

                Rectangle {
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                    Layout.preferredWidth: horizontalMode && hourText.length == 1 ? timeRoot.horizontalFontWidth / 2 : timeRoot.horizontalFontWidth
                    Layout.fillHeight: true
                    color: "transparent"

                    Label {
                        id: hour
                        width: parent.width
                        height: parent.height
                        font.capitalization: Font.AllUppercase
                        font.family: "Noto Sans"
                        font.bold: true
                        font.weight: Font.Bold
                        font.pixelSize: horizontalMode ? timeRoot.horizontalFontWidth : parent.height
                        horizontalAlignment: horizontalMode ? Text.AlignRight : Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        color: Kirigami.Theme.textColor
                        renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)

                        Component.onCompleted: {
                            var setHour
                            if(hourText.length == 1 && horizontalMode) {
                                setHour = setHour + "  "
                                hour.text = setHour
                            } else {
                                hour.text = hourText
                            }
                        }
                    }
                }

                Item {
                    id: colons
                    Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter
                    Layout.fillHeight: true
                    Layout.preferredWidth: parent.width * 0.10
                    height: parent.height
                    visible: horizontalMode ? 1 : 0
                    enabled: horizontalMode ? 1 : 0
                }

                Rectangle {
                    Layout.preferredWidth: timeRoot.horizontalFontWidth
                    Layout.fillHeight: true
                    color: "transparent"

                    Label {
                        id: minute
                        width: parent.width
                        height: parent.height
                        font.capitalization: Font.AllUppercase
                        font.family: "Noto Sans"
                        font.bold: true
                        font.weight: Font.Bold
                        font.pixelSize: horizontalMode ? timeRoot.horizontalFontWidth : parent.height
                        horizontalAlignment: horizontalMode ? Text.AlignLeft : Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        color: Kirigami.Theme.highlightColor
                        renderType: height > 40 ? Text.QtRendering : (Screen.devicePixelRatio % 1 !== 0 ? Text.QtRendering : Text.NativeRendering)

                        Component.onCompleted: {
                            var setMin
                            if(minuteText.length == 1 && horizontalMode) {
                                setMin = setMin + "  "
                                minute.text = setMin
                            } else {
                                minute.text = minuteText
                            }
                        }
                    }
                }
            }
        }
    }
}
