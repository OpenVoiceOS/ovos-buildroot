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

ItemDelegate {
    id: alarmOverViewCard
    implicitHeight: activeAlarmsViews.height - (headerLayout.height / 2)
    implicitWidth: activeAlarmsViews.count == 1 ? activeAlarmsViews.width : activeAlarmsViews.width / 2.5

    background: Rectangle {
        color: Kirigami.Theme.backgroundColor
        border.color: Kirigami.Theme.highlightColor
        border.width: 1
        radius: 6
    }

    contentItem: Item {

        AlarmBoxView {
            id: alarmCardColumn
            anchors.top: parent.top
            anchors.margins: Mycroft.Units.gridUnit / 4
            anchors.left: parent.left
            anchors.right: parent.right
            height: parent.height * 0.7
            alarmName: model.alarmName
            alarmTime: model.alarmTime
            alarmAmPm: model.alarmAmPm
            alarmExpired: model.alarmExpired
        }

        Kirigami.Separator {
            id: alarmCardColumnSeparator
            anchors.top: alarmCardColumn.bottom
            anchors.topMargin: Mycroft.Units.gridUnit / 4
            anchors.left: parent.left
            anchors.right: parent.right
            height: 1
        }

        AlarmButtonView {
            id: alarmCardColumnThree
            anchors.top: alarmCardColumnSeparator.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.topMargin: Mycroft.Units.gridUnit / 4
            height: parent.height * 0.27
            alarmName: model.alarmName
            alarmIndex: model.alarmIndex
            alarmContext: "overview"
            alarmExpired: sessionData.alarmExpired
        }
    }
}