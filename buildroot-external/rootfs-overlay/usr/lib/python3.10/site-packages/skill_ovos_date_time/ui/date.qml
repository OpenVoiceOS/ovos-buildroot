import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0

Mycroft.CardDelegate {
    id: dateRoot
    cardRadius: 10
    cardBackgroundOverlayColor: Qt.rgba(Kirigami.Theme.highlightColor.r, Kirigami.Theme.highlightColor.g, Kirigami.Theme.highlightColor.b, 0.5)
    property bool horizontalMode: width > height ? 1 : 0

    Label {
        id: weekday
        anchors.top: parent.top
        anchors.bottom: dateContentsArea.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: Mycroft.Units.gridUnit / 2
        anchors.rightMargin: Mycroft.Units.gridUnit / 2
        fontSizeMode: Text.Fit
        minimumPixelSize: horizontalMode ? height * 0.3 : width * 0.05
        font.pixelSize: horizontalMode ? height * 0.9 : width * 0.7
        renderType: Text.NativeRendering
        font.family: "Noto Sans Display"
        font.styleName: "Black"
        font.capitalization: Font.AllUppercase
        text: sessionData.weekday_string
        elide: Text.ElideRight
        maximumLineCount: 1
        color: Kirigami.Theme.textColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Label {
        id: year
        anchors.top: dateContentsArea.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: Mycroft.Units.gridUnit / 2
        anchors.rightMargin: Mycroft.Units.gridUnit / 2
        fontSizeMode: Text.Fit
        minimumPixelSize: horizontalMode ? height * 0.3 : width * 0.05
        font.pixelSize: horizontalMode ? height * 0.9 : width * 0.7
        renderType: Text.NativeRendering
        font.family: "Noto Sans Display"
        font.styleName: "Black"
        font.capitalization: Font.AllUppercase
        text: sessionData.year_string
        elide: Text.ElideRight
        maximumLineCount: 1
        color: Kirigami.Theme.textColor
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Rectangle {
        id: dateContentsArea
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.right: parent.right
        color: Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
        height: parent.height / 2

        Label {
            id: day
            anchors.fill: parent
            anchors.margins: Mycroft.Units.gridUnit
            fontSizeMode: Text.Fit
            minimumPixelSize: horizontalMode ? height * 0.3 : width * 0.05
            font.pixelSize: horizontalMode ? height * 0.9 : width * 0.7
            elide: Text.ElideRight
            maximumLineCount: 1
            font.family: "Noto Sans Display"
            font.styleName: "Bold"
            text: sessionData.daymonth_string
            color: Kirigami.Theme.textColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
