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

import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.3
import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.plasma.components 2.0 as PlasmaComponents
import org.kde.kirigami 2.8 as Kirigami
import org.kde.plasma.networkmanagement 0.2 as PlasmaNM
import Mycroft 1.0 as Mycroft
import QtGraphicalEffects 1.0

Rectangle {
    id: podControl
    color: Qt.lighter(Kirigami.Theme.backgroundColor, 0.8)
    border.width: 1
    border.color: Qt.darker(Kirigami.Theme.textColor, 0.5)
    radius: 10
    property var podIcon
    property var podMainText
    property var podSubText

    RowLayout {
        id: podLayout
        anchors.fill: parent
        anchors.leftMargin: Mycroft.Units.gridUnit
        anchors.rightMargin: Mycroft.Units.gridUnit

        Item {
            id: podIconItemArea
            Layout.preferredWidth: Mycroft.Units.gridUnit * 3
            Layout.maximumWidth: Mycroft.Units.gridUnit * 3
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter

            Kirigami.Icon {
                id: podIconItem
                source: podControl.podIcon                
                anchors.centerIn: parent
                width: parent.height * 0.75
                height: parent.height * 0.75

                ColorOverlay {
                    id: podIconOverlay
                    color: Kirigami.Theme.textColor
                    source: podIconItem
                    anchors.fill: parent
                }
            }
        }

        Label {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            text: podControl.podMainText
            color: Kirigami.Theme.textColor
            horizontalAlignment: Text.AlignLeft
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: parent.height * 0.4
            elide: Text.ElideRight
        }

        Label {
            id: podSubTextItemArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            text: podControl.podSubText
            color: Kirigami.Theme.textColor
            horizontalAlignment: Text.AlignRight
            verticalAlignment: Text.AlignVCenter
            font.pixelSize: parent.height * 0.4
            elide: Text.ElideRight
        }
    }
}
