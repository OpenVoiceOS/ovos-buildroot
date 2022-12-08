import QtQuick.Layouts 1.4
import QtQuick 2.9
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Rectangle {
    id: dayMonthDisplay
    color: "transparent"
    property bool verticalMode: false

    function update_dateFormat(longShortMonth) {
        var longShortMonth = longShortMonth
        switch(idleRoot.dateFormat) {
            case "DMY":
                return sessionData.weekday_string.substring(0,3) + " " + sessionData.day_string + " " +  longShortMonth + ", " + sessionData.year_string
                break
            case "MDY":
                return sessionData.weekday_string.substring(0,3) + " " + longShortMonth + " " + sessionData.day_string + ", " + sessionData.year_string
                break
            case "YMD":
                return sessionData.year_string + ", " + longShortMonth + " " + sessionData.weekday_string.substring(0,3) + " " + sessionData.day_string
                break
            default:
                return sessionData.weekday_string.substring(0,3) + " " + sessionData.day_string + " " +  longShortMonth + ", " + sessionData.year_string
                break
        }
    }

    Label {
        id: weekday
        width: parent.width
        height: parent.height
        fontSizeMode: Text.Fit
        minimumPixelSize: dayMonthDisplay.verticalMode ? 30 : 50
        font.pixelSize: Math.round(parent.height * 0.725)
        horizontalAlignment: dayMonthDisplay.verticalMode ? Text.AlignHCenter : (idleRoot.rtlMode ? Text.AlignRight : Text.AlignLeft)
        verticalAlignment: Text.AlignVCenter
        maximumLineCount: 1
        elide: idleRoot.rtlMode ? Text.ElideLeft : Text.ElideRight
        font.weight: Font.DemiBold
        font.letterSpacing: 1.1
        property var longShortMonth: horizontalMode ? (sessionData.month_string ? sessionData.month_string : "" ) : (sessionData.month_string ? sessionData.month_string.substring(0,3) : "")
        text: sessionData.year_string && sessionData.weekday_string ? dayMonthDisplay.update_dateFormat(longShortMonth) : ""
        color: "white"
        layer.enabled: true
        layer.effect: DropShadow {
            verticalOffset: 4
            color: idleRoot.shadowColor
            radius: 11
            spread: 0.4
            samples: 16
        }
    }
}
