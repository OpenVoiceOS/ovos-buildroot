import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

WeatherDelegate {
    id: root
    weatherCode: sessionData.weatherCode ? sessionData.weatherCode : sessionData.forecast.all[0].weatherCondition

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
            id: dailyLabelTop
            font.styleName: "Bold"
            font.pixelSize: parent.height * 0.70
            anchors.left: colSpt.right
            anchors.leftMargin: Kirigami.Units.largeSpacing
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            width: parent.width - (Kirigami.Units.largeSpacing + 1)
            height: parent.height
            color: dayNightTime == "day" ? "black" : "white"
            text: qsTr("DAILY")
        }
    }

    Row {
        anchors.top: locBoxDetailsArea.bottom
        anchors.topMargin: Mycroft.Units.gridUnit * 2
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        spacing: Kirigami.Units.smallSpacing * 1.5

        DailyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.forecast.all[0]
        }
        DailyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.forecast.all[1]
        }
        DailyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.forecast.all[2]
        }
        DailyForecastColumnDelegate {
            width: parent.width / 4
            height: parent.height
            forecastData: sessionData.forecast.all[3]
        }
    }
}
