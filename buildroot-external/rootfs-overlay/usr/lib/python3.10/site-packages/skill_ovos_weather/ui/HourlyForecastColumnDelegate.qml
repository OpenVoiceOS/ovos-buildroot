import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

Column {
    property var forecastData

    onForecastDataChanged: {
        console.log(JSON.stringify(forecastData))
    }

    Item {
        width: parent.width
        height: parent.height * 0.25
        anchors.left: parent.left
        anchors.right: parent.right

        Image {
            anchors.fill: parent
            source: Qt.resolvedUrl(getWeatherImagery(forecastData.weatherCondition))
            fillMode: Image.PreserveAspectFit

            onSourceChanged: {
                console.log(source)
            }
        }
    }

    Label {
        anchors.left: parent.left
        anchors.right: parent.right

        height: parent.height * 0.25
        horizontalAlignment: Text.AlignHCenter
        font.weight: Font.Bold
        font.pixelSize: width * 0.3
        color: dayNightTime == "day" ? "black" : "white"
        text: forecastData.time
    }

    Label {
        anchors.left: parent.left
        anchors.right: parent.right
        horizontalAlignment: Text.AlignHCenter

        font.weight: Font.Bold
        font.pixelSize: width * 0.3
        height: parent.height * 0.25
        color: dayNightTime == "day" ? "black" : "white"
        text: forecastData.temperature + "°"
    }

    Label {
        anchors.left: parent.left
        anchors.right: parent.right
        horizontalAlignment: Text.AlignHCenter

        font.styleName: "Thin"
        font.pixelSize: width * 0.25
        height: parent.height * 0.25
        color: dayNightTime == "day" ? "black" : "white"
        text: forecastData.precipitation + "%"
    }
}
