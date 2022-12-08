import QtQuick 2.9
import QtGraphicalEffects 1.0

Rectangle {
    id: control
    width: parent.width
    height: parent.height
    property real value: 0
    property alias text: timeText.text
    color: "transparent"
    border.color: timerCard.primaryColor
    border.width: 4
    radius: parent.width / 2

    SequentialAnimation on color {
            id: expireAnimationBg
            running: modelData.expired
            loops: Animation.Infinite
            PropertyAnimation {
                from: timerCard.backgroundBorderColor;
                to: "transparent";
                duration: 1000
            }
            PropertyAnimation {
                from: "transparent";
                to: timerCard.backgroundBorderColor;
                duration: 1000
            }
        }


    Text {
        id: timeText
        color: timerCard.expiredColor
        fontSizeMode: Text.Fit
        minimumPixelSize: 5
        font.pixelSize: 72
        anchors.fill: parent
        anchors.margins: parent.width * 0.15
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter

        SequentialAnimation on opacity {
            id: expireAnimation
            running: modelData.expired
            loops: Animation.Infinite
            PropertyAnimation {
                from: 1;
                to: 0;
                duration: 1000
            }
            PropertyAnimation {
                from: 0;
                to: 1;
                duration: 1000
            }
        }
    }

    Row{
        id: circle
        property color circleColor: "transparent"
        property color borderColor: timerCard.secondaryColor
        property int borderWidth: 10
        anchors.fill: parent
        anchors.margins: -6
        width: parent.width //-10
        height: width

        Item{
            width: parent.width/2
            height: parent.height
            clip: true

            Item{
                id: part1
                width: parent.width
                height: parent.height
                clip: true
                rotation: value > 0.5 ? 360 : 180 + 360*value
                transformOrigin: Item.Right

                Rectangle{
                    width: circle.width-(circle.borderWidth*2)
                    height: circle.height-(circle.borderWidth*2)
                    radius: width/2
                    x:circle.borderWidth
                    y:circle.borderWidth
                    color: circle.circleColor
                    border.color: circle.borderColor
                    border.width: circle.borderWidth
                    smooth: true
                }
            }
        }

        Item{
            width: parent.width/2
            height: parent.height
            clip: true

            Item{
                id: part2
                width: parent.width
                height: parent.height
                clip: true
                rotation: value <= 0.5 ? 180 : 360*(value)
                transformOrigin: Item.Left

                Rectangle{
                    width: circle.width-(circle.borderWidth*2)
                    height: circle.height-(circle.borderWidth*2)
                    radius: width/2
                    x: -width/2
                    y: circle.borderWidth
                    color: circle.circleColor
                    border.color: circle.borderColor
                    border.width: circle.borderWidth
                    smooth: true
                }
            }
        }
    }
}

