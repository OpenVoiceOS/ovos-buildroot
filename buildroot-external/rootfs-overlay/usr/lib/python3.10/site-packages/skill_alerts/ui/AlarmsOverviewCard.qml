/*
 * Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft
import org.kde.kirigami 2.11 as Kirigami

Mycroft.CardDelegate {
    id: alarmFrame
    property int activeAlarmCount: sessionData.activeAlarmCount
    property int previousCount: 0

    function getEndPos(){
        var ratio = 1.0 - alarmFlick.visibleArea.widthRatio;
        var endPos = alarmFlick.contentWidth * ratio;
        return endPos;
    }

    function scrollToEnd(){
        alarmFlick.contentX = getEndPos();
    }

    onActiveAlarmCountChanged: {
        if(activeAlarmCount == activeAlarmsViews.count){
            if(previousCount < activeAlarmCount) {
                previousCount = previousCount + 1
            }
            console.log(activeAlarmCount)
        }
    }

    onPreviousCountChanged: {
        scrollToEnd()
    }

    ColumnLayout {
        id: headerLayout
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: Mycroft.Units.gridUnit * 3

        Kirigami.Heading {            
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Alarms Overview"
            level: 2
            color: Kirigami.Theme.textColor
        }

        Kirigami.Separator {            
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: Kirigami.Theme.highlightColor
        }
    }

    Flickable {
        id: alarmFlick
        anchors.top: headerLayout.bottom
        anchors.topMargin: Mycroft.Units.gridUnit / 2
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        contentWidth: activeAlarmsViews.count == 1 ? width : width / 2.75 * activeAlarmsViews.count
        contentHeight: parent.height - headerLayout.height
        clip: true

        Row {
            id: alarmsViewLayout
            width: parent.width
            height: parent.height
            spacing: Mycroft.Units.gridUnit / 3

            Repeater {
                id: activeAlarmsViews
                width: alarmFlick.width
                height: parent.height
                model: sessionData.activeAlarms
                delegate: AlarmsOverviewDelegate {
                }
                onItemRemoved: {
                    alarmFlick.returnToBounds()
                }
            }
        }
    }
}