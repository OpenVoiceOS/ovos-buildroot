import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

WeatherDelegate {
    id: root
    weatherCode: sessionData.weatherCode

    Column {
        id: locBoxDetailsArea
        anchors.top: parent.top
        anchors.right: parent.right
        width: parent.width / 4
        height: locBoxHeight + locBoxHeight * 0.5
        spacing: Kirigami.Units.smallSpacing * 0.5

        Row {
            id: windRow
            spacing: Mycroft.Units.gridUnit
            height: parent.height / 2
            width: parent.width

            Item {
                id: windIconBox
                width: parent.width / 2
                height: parent.height

                Image {
                    id: windIcon
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.height * 0.90
                    height: width
                    fillMode: Image.PreserveAspectFit
                    source: "images/wind.svg"
                }
            }

            Item {
                width: parent.width - (windIconBox.width + Mycroft.Units.gridUnit)
                height: parent.height
                anchors.bottom: parent.bottom

                Label {
                    id: windSpeed
                    width: parent.width
                    height: parent.height
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.weight: Font.Bold
                    font.pixelSize: parent.width > parent.height ? height * 0.90 : width * 0.90
                    color: dayNightTime == "day" ? "black" : "white"
                    text: sessionData.windSpeed
                }
            }
        }

        Kirigami.Separator {
            width: parent.width
            height: 1
        }

        Row {
            id: humidityRow
            spacing: Mycroft.Units.gridUnit
            height: parent.height / 2
            width: parent.width

            Item {
                id: humidityIconBox
                width: parent.width / 2
                height: parent.height

                Image {
                    id: humidityIcon
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: parent.height * 0.90
                    height: width
                    fillMode: Image.PreserveAspectFit
                    source: "images/humidity.svg"
                }
            }

            Item {
                width: parent.width - (humidityIconBox.width + Mycroft.Units.gridUnit)
                height: parent.height

                Label {
                    id: humidityPercentage
                    width: parent.width
                    height: parent.height
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.weight: Font.Bold
                    font.pixelSize: parent.width > parent.height ? height * 0.90 : width * 0.90
                    color: dayNightTime == "day" ? "black" : "white"
                    text: sessionData.humidity
                }
            }
        }
    }

    Rectangle {
        anchors.top: parent.top
        anchors.topMargin: root.locBoxHeight
        anchors.bottom: weatherInfoBox.top
        color: "transparent"
        width: parent.width

        LottieAnimation {
            id: weatherAnimation
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.height
            height: width
            source: Qt.resolvedUrl(getWeatherAnimation(sessionData.weatherCode))
            fillMode: Image.PreserveAspectFit
            running: true
            loops: Animation.Infinite
        }
    }


    Rectangle {
        id: weatherInfoBox
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        color: "transparent"
        height: parent.height / 2

        Item {
            anchors.left: parent.left
            anchors.right: sept1.left
            anchors.rightMargin: Mycroft.Units.gridUnit
            height: parent.height

            Label {
                id: temperature
                width: parent.width
                height: parent.height
                anchors.centerIn: parent
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.weight: Font.Bold
                font.pixelSize: parent.width > parent.height ? height * 0.60 : width * 0.60
                rightPadding: -font.pixelSize * 0.1
                color: dayNightTime == "day" ? "black" : "white"
                text: sessionData.currentTemperature + "°"
            }
        }

        Kirigami.Separator {
            id: sept1
            width: 1
            height: parent.height * 0.60
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenter: parent.horizontalCenter
        }

        ColumnLayout {
            anchors.left: sept1.right
            anchors.right: parent.right
            anchors.leftMargin: Mycroft.Units.gridUnit
            height: parent.height

            Row {
                Layout.fillWidth: true
                Layout.preferredHeight: parent.height * 0.50
                spacing: parent.width > parent.height ? Mycroft.Units.gridUnit * 2 : Mycroft.Units.gridUnit

                Rectangle {
                    id: maxIconBox
                    width: parent.width / 4
                    height: parent.height
                    color: "transparent"


                    Kirigami.Icon {
                        id: maxIcon
                        source: "go-up"
                        width: parent.width * 0.75
                        height: width
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        color: dayNightTime == "day" ? "black" : "white"
                    }
                }

                Rectangle {
                    width: parent.width - maxIconBox.width
                    height: parent.height
                    color: "transparent"


                    Label {
                        id: maxTemp
                        width: parent.width
                        height: parent.height
                        font.weight: Font.Bold
                        font.pixelSize: parent.width > parent.height ? parent.height * 0.65 : parent.width * 0.50
                        rightPadding: -font.pixelSize * 0.1
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        color: dayNightTime == "day" ? "black" : "white"
                        text: sessionData.highTemperature + "°"
                    }
                }
            }

            Row {
                Layout.fillWidth: true
                Layout.preferredHeight: parent.height * 0.50
                spacing: parent.width > parent.height ? Mycroft.Units.gridUnit * 2 : Mycroft.Units.gridUnit

                Rectangle {
                    id: minIconBox
                    width: parent.width / 4
                    height: parent.height
                    color: "transparent"

                    Kirigami.Icon {
                        id: minIcon
                        source: "go-down"
                        width: parent.width * 0.75
                        height: width
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        color: dayNightTime == "day" ? "black" : "white"
                    }
                }

                Rectangle {
                    width: parent.width - minIconBox.width
                    height: parent.height
                    color: "transparent"

                    Label {
                        id: minTemp
                        width: parent.width
                        height: parent.height
                        font.pixelSize: parent.width > parent.height ? parent.height * 0.65 : parent.width * 0.50
                        rightPadding: -font.pixelSize * 0.1
                        font.weight: Font.Thin
                        font.styleName: "Thin"
                        horizontalAlignment: Text.AlignLeft
                        verticalAlignment: Text.AlignVCenter
                        color: dayNightTime == "day" ? "black" : "white"
                        text: sessionData.lowTemperature + "°"
                    }
                }
            }
        }
    }
}
