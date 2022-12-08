/*
 * Copyright 2018 Aditya Mehra <aix.m@outlook.com>
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

import QtQuick.Layouts 1.12
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.11 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import QtGraphicalEffects 1.0
import Mycroft 1.0 as Mycroft

Button {
    id: backendButtonControl
    property string backendName
    property string backendIcon
    property string backendType
    property bool horizontalMode: false

    background: Rectangle {
        color: backendButtonControl.down ? "transparent" :  Kirigami.Theme.highlightColor
        border.width: 6
        border.color: Qt.darker(Kirigami.Theme.highlightColor, 1.2)
        radius: 10

        Rectangle {
            width: parent.width - 32
            height: parent.height - 32
            anchors.centerIn: parent
            color: backendButtonControl.down ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.backgroundColor, 1.5)
            radius: 10
        }
    }

    contentItem: Loader {
        id: backendButtonLoader
        sourceComponent: backendButtonControl.horizontalMode ? horizontalButtonContent : verticalButtonContent
        onLoaded: {
            backendButtonLoader.item.backendName = backendButtonControl.backendName
            backendButtonLoader.item.backendIcon = backendButtonControl.backendIcon
        }
    }

    onClicked: {
        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("sounds/clicked.wav"))
        triggerGuiEvent("mycroft.device.set.backend",
        {"backend": backendButtonControl.backendType})
    }

    Component {
        id: horizontalButtonContent

        ColumnLayout {
            id: backendButtonContentsLayout
            spacing: Mycroft.Units.gridUnit
            anchors.fill: parent
            property string backendName
            property string backendIcon

            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: parent.height < 300 ? 0 : Mycroft.Units.gridUnit * 2
            }

            Item {
                Layout.preferredWidth: parent.width - Kirigami.Units.iconSizes.large * 4
                Layout.preferredHeight: parent.width - Kirigami.Units.iconSizes.large * 4
                Layout.minimumWidth: parent.height < 300 ? Kirigami.Units.iconSizes.large * 1.4 : Kirigami.Units.iconSizes.large * 2
                Layout.minimumHeight: parent.height < 300 ? Kirigami.Units.iconSizes.large * 1.4 : Kirigami.Units.iconSizes.large * 2
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom

                Kirigami.Icon {
                    width: parent.width * 0.8
                    height: parent.height * 0.8
                    anchors.centerIn: parent
                    source: backendButtonContentsLayout.backendIcon
                }
            }

            Label {
                Layout.fillWidth: true                
                Layout.fillHeight: true
                Layout.leftMargin: Mycroft.Units.gridUnit 
                Layout.rightMargin: Mycroft.Units.gridUnit
                Layout.alignment: Qt.AlignHCenter | Qt.AlignTop

                verticalAlignment: Text.AlignTop
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                elide: Text.ElideRight
                font.pixelSize: 32
                minimumPixelSize: 8
                fontSizeMode: Text.Fit
                text: backendButtonContentsLayout.backendName
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
        }
    }

    Component {
        id: verticalButtonContent
        
        RowLayout {
            id: backendButtonContentsLayout
            spacing: Mycroft.Units.gridUnit
            anchors.fill: parent
            property string backendName
            property string backendIcon

            Kirigami.Icon {
                Layout.preferredWidth: parent.height * 0.5
                Layout.preferredHeight: width
                Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                Layout.leftMargin: Mycroft.Units.gridUnit / 2
                source: backendButtonContentsLayout.backendIcon
            }

            Label {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.leftMargin: Mycroft.Units.gridUnit / 2
                Layout.rightMargin: Mycroft.Units.gridUnit / 2

                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 32
                minimumPixelSize: 16
                fontSizeMode: Text.Fit
                text: backendButtonContentsLayout.backendName
            }
        }
    }
}