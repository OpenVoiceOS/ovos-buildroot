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
    property int currentIndex: 0

    Keys.onLeftPressed: {
        if (currentIndex > 0) {
            currentIndex = Math.max(0, currentIndex - 1);
            timerFlick.contentX = timerViewLayout.children[currentIndex].x
        }
    }

    Keys.onRightPressed: {
        if (currentIndex < timerCount - 1) {
            currentIndex = Math.min(timerCount - 1, currentIndex + 1);
            timerFlick.contentX = timerViewLayout.children[currentIndex].x - timerFlick.width / 2.5
        }
    }

    onCurrentIndexChanged: {
        timerViewLayout.children[currentIndex].forceActiveFocus()
    }

    function getEndPos(){
        var ratio = 1.0 - timerFlick.visibleArea.widthRatio;
        var endPos = timerFlick.contentWidth * ratio;
        return endPos;
    }

    function scrollToEnd(){
        timerFlick.contentX = getEndPos();
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
        scrollToEnd()
    }

    Flickable {
        id: timerFlick
        anchors.fill: parent
        contentWidth: timerViews.count == 1 ? width : width / 2.5 * timerViews.count
        contentHeight: parent.height
        clip: true

        Row {
            id: timerViewLayout
            width: parent.width
            height: parent.height
            spacing: Mycroft.Units.gridUnit / 3

            Repeater {
                id: timerViews
                width: timerFlick.width
                height: parent.height
                model: sessionData.activeTimers.timers
                delegate: TimerCard {}
                onItemRemoved: {
                    timerFlick.returnToBounds()
                }
            }
        }
    }
}
