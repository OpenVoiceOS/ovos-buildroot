import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import QtGraphicalEffects 1.0
import QtQuick.Shapes 1.12
import QtQml.Models 2.12
import org.kde.kirigami 2.9 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.CardDelegate {
    id: timerFrame
    property int timerCount: sessionData.activeTimerCount
    property int previousCount: 0
    property bool horizontalMode: parent.width >= parent.height ? 1 : 0

    function getEndPos(){
        var ratio = 1.0 - timerFlick.visibleArea.widthRatio;
        var endPos = timerFlick.contentWidth * ratio;
        return endPos;
    }

    function getEndPosYaxis(){
        var ratio = 1.0 - timerFlick.visibleArea.heightRatio;
        var endPos = timerFlick.contentHeight * ratio;
        return endPos;
    }

    function scrollToEnd(){
        timerFlick.contentX = getEndPos();
    }

    function scrollToBottom(){
        timerFlick.contentY = getEndPosYaxis();
    }

    onTimerCountChanged: {
        if(timerCount == timerViews.count){
            if(previousCount < timerCount) {
                previousCount = previousCount + 1
            }
            console.log(timerCount)
        }
    }

    onPreviousCountChanged: {
        if(timerFrame.horizontalMode){
            scrollToEnd()
        } else {
            scrollToBottom()
        }
    }

    Flickable {
        id: timerFlick
        anchors.fill: parent
        contentWidth: timerFrame.horizontalMode ? (timerViews.count == 1 ? width : width / 2.5 * timerViews.count) : width
        contentHeight: timerFrame.horizontalMode ? parent.height : timerViewLayout.implicitHeight
        clip: true

        Grid {
            id: timerViewLayout
            width: parent.width
            height: parent.height
            spacing: Mycroft.Units.gridUnit / 3
            columns: timerFrame.horizontalMode ? timerViews.count : 1

            Repeater {
                id: timerViews
                width: timerFlick.width
                height: parent.height
                model: sessionData.activeTimers.timers
                delegate: TimerCard {
                    implicitHeight: timerFrame.horizontalMode ? timerViews.height : (timerViews.count == 1 ? timerFlick.height : timerFlick.height / 2.5)
                    implicitWidth: timerFrame.horizontalMode ? (timerViews.count == 1 ? timerViews.width : timerViews.width / 2.5) : timerViews.width
                }
                onItemRemoved: {
                    timerFlick.returnToBounds()
                }
            }
        }
    }
}
