import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import "backgrounds"

Mycroft.Delegate {
    id: root
    skillBackgroundColorOverlay: "transparent"
    property string dayNightTime: "day"
    property int gridUnit: Mycroft.Units.gridUnit
    property int locBoxHeight: locationBox.height
    property int locBoxWidth: locLabel.contentWidth
    property alias dateTimeLabelText: dtLabel.text
    property var weatherCode
    property var bgStyle

    fillWidth: true
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0

    onWeatherCodeChanged: {
        root.dayNightTime = getDayNight(root.weatherCode)
        root.bgStyle = getBackgroundStyle(root.weatherCode)
    }

    background: Item {
        Image {
            id: backgroundImage
            anchors.fill: parent
            fillMode: Image.PreserveAspectCrop
            source: Qt.resolvedUrl("images/day.jpg")

            Rectangle {
                anchors.fill: parent
                gradient: Gradient {
                    GradientStop {position: 0.0; color: dayNightTime == "day" ? Qt.rgba(0.25, 0.7, 1, 1) : Qt.rgba(0, 0, 0.05, 0.95)}
                    GradientStop {position: 1.0; color: dayNightTime == "day" ? Qt.rgba(0, 0.4, 0.8, 0.95) : Qt.rgba(0, 0, 0.3, 0.55)}
                }
            }
            Loader {
                id: background
                anchors.fill: parent
                source: root.bgStyle
                onSourceChanged: background.item["inView"] = parent.visible
            }
        }
    }

    contentItem: Item {
        z: 2
        anchors.fill: parent
        anchors.margins: Mycroft.Units.gridUnit * 2

        Rectangle {
            id: locationBox
            anchors.top: parent.top
            anchors.left: parent.left
            color: "transparent"
            width: parent.width
            height: parent.height * 0.15

            Label {
                id: dtLabel
                anchors.top: parent.top
                anchors.bottomMargin: Mycroft.Units.gridUnit * 0.25
                anchors.left: parent.left
                color: dayNightTime == "day" ? "black" : "white"
                font.bold: true
                font.pixelSize: parent.width > parent.height ? parent.height * 0.35 : parent.width * 0.35
                minimumPixelSize: 5
                fontSizeMode: Text.Fit
                text: sessionData.currentTimezone
            }

            Label {
                id: locLabel
                anchors.top: dtLabel.bottom
                anchors.left: parent.left
                minimumPixelSize: 5
                font.pixelSize: parent.width > parent.height ? parent.height * 0.35 : parent.width * 0.35
                fontSizeMode: Text.Fit
                color: dayNightTime == "day" ? "black" : "white"
                text: sessionData.weatherLocation
            }
        }
    }

    function getBackgroundStyle(weathercode) {
        switch(weathercode) {
            case 0:
            case 1:
            case 2:
            case 3:
            case 4:
            case 5:
            case 6:
            case 7:
            case 16:
            case 17:
                return "backgrounds/Simple.qml"
                break
            case 8:
            case 9:
            case 10:
            case 11:
            case 12:
            case 13:
                return "backgrounds/Rainy.qml"
                break
            case 14:
            case 15:
                return "backgrounds/Snowy.qml"
                break
        }
    }

    function getDayNight(weathercode) {
        switch(weathercode) {
            case 0:
            case 2:
            case 4:
            case 6:
            case 8:
            case 10:
            case 12:
            case 14:
            case 16:
                backgroundImage.source = Qt.resolvedUrl("images/day.jpg")
                return "day"
                break
            case 1:
            case 3:
            case 5:
            case 7:
            case 9:
            case 11:
            case 13:
            case 15:
            case 17:
                backgroundImage.source = Qt.resolvedUrl("images/night.jpg")
                return "night"
                break
        }
    }

    function getWeatherImagery(weathercode) {
        switch(weathercode) {
        case 0:
            // Clear Sky Day
            return "images/sun.svg";
            break
        case 1:
            // Clear Sky Night
            return "images/moon.svg";
            break
        case 2:
            // Few Clouds Day
            return "images/partial_clouds_day.svg";
            break
        case 3:
            // Few Clouds Night
            return "images/partial_clouds_night.svg";
            break
        case 4:
            // Scattered Clouds Day
            return "images/clouds.svg";
            break
        case 5:
            // Scattered Clouds Night
            return "images/clouds.svg";
            break
        case 6:
            // Broken Clouds Day
            return "images/partial_clouds_day.svg";
            break
        case 7:
            // Broken Clouds Night
            return "images/partial_clouds_day.svg";
            break
        case 8:
            // Shower Rain Day
            return "images/rain.svg"
            break
        case 9:
            // Shower Rain Night
            return "images/rain.svg"
            break
        case 10:
            // Rain Day
            return "images/rain.svg"
            break
        case 11:
            // Rain Night
            return "images/rain.svg"
            break
        case 12:
            // Thunderstorm Day
            return "images/storm.svg"
            break
        case 13:
            // Thunderstorm Night
            return "images/storm.svg"
            break
        case 14:
            // Snow Day
            return "images/snow.svg"
            break
        case 15:
            // Snow Night
            return "images/snow.svg"
            break
        case 16:
            // Mist Day
            return "images/fog.svg"
            break
        case 17:
            // Mist Night
            return "images/fog.svg"
        }
    }

     function getWeatherAnimation(weathercode) {
        switch(weathercode) {
        case 0:
            // Clear Sky Day
            return "animations/sun.json";
            break
        case 1:
            // Clear Sky Night
            return "animations/night.json";
            break
        case 2:
            // Few Clouds Day
            return "animations/partial_clouds.json";
            break
        case 3:
            // Few Clouds Night
            return "animations/partial_clouds.json";
            break
        case 4:
            // Scattered Clouds Day
            return "animations/clouds.json";
            break
        case 5:
            // Scattered Clouds Night
            return "animations/clouds.json";
            break
        case 6:
            // Broken Clouds Day
            return "animations/partial_clouds.json";
            break
        case 7:
            // Broken Clouds Night
            return "animations/partial_clouds.json";
            break
        case 8:
            // Shower Rain Day
            return "animations/rain.json"
            break
        case 9:
            // Shower Rain Night
            return "animations/rain.json"
            break
        case 10:
            // Rain Day
            return "animations/rain.json"
            break
        case 11:
            // Rain Night
            return "animations/rain.json"
            break
        case 12:
            // Thunderstorm Day
            return "animations/storm.json"
            break
        case 13:
            // Thunderstorm Night
            return "animations/storm.json"
            break
        case 14:
            // Snow Day
            return "animations/snow.json"
            break
        case 15:
            // Snow Night
            return "animations/snow.json"
            break
        case 16:
            // Mist Day
            return "animations/fog.json"
            break
        case 17:
            // Mist Night
            return "animations/fog.json"
        }
    }
}
