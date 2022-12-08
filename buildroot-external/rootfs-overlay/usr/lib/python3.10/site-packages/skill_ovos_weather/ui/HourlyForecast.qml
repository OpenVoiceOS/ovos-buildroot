import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

WeatherDelegate {
    id: root
    weatherCode: sessionData.weatherCode ? sessionData.weatherCode : sessionData.hourlyForecast.hours[0].weatherCondition

    Rectangle {
        id: locBoxDetailsArea
        anchors.top: parent.top
        anchors.topMargin: locBoxHeight
        anchors.left: parent.left
        width: locBoxWidth
        height: locBoxHeight / 2
        color: dayNightTime == "day" ? "white" : "black"

        Kirigami.Separator {
            id: colSpt
            anchors.left: parent.left
            width: 5
            height: parent.height
            color: dayNightTime == "day" ? "black" : "white"
        }

        Label {
            id: hourlyLabelTop
            font.styleName: "Bold"
            font.pixelSize: parent.height * 0.70
            anchors.left: colSpt.right
            anchors.leftMargin: Kirigami.Units.largeSpacing
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            width: parent.width - (Kirigami.Units.largeSpacing + 1)
            height: parent.height
            color: dayNightTime == "day" ? "black" : "white"
            text: qsTr("HOURLY")
        }
    }

    Row {
        anchors.top: locBoxDetailsArea.bottom
        anchors.topMargin: Mycroft.Units.gridUnit * 2
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        spacing: Kirigami.Units.smallSpacing * 1.5

        HourlyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.hourlyForecast.hours[0]
        }
        HourlyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.hourlyForecast.hours[1]
        }
        HourlyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.hourlyForecast.hours[2]
        }
        HourlyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.hourlyForecast.hours[3]
        }
    }
}
