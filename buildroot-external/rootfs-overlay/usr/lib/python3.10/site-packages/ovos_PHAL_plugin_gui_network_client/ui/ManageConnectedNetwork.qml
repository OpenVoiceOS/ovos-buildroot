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

Rectangle {
    id: manageConnectedNetworkView

    Kirigami.Theme.inherit: false
    Kirigami.Theme.colorSet: Kirigami.Theme.Complementary
    color: Kirigami.Theme.backgroundColor
    property var connection: sessionData.connectionDetails ? sessionData.connectionDetails : ""
    property string networkName: connection.networkName ? connection.networkName : ""
    property string networkSecurity: connection.networkSecurity ? connection.networkSecurity : ""
    property string networkState: "Connected"
    property int networkStrength: connection.networkStrength ? connection.networkStrength : 0
    property string networkSpeed: connection.networkSpeed ? connection.networkSpeed : ""
    property string networkAddress: sessionData.ipAddress ? sessionData.ipAddress : "127.0.0.1"

    Item {
        id: viewTopArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: Mycroft.Units.gridUnit / 2 
        anchors.leftMargin: Mycroft.Units.gridUnit * 2
        anchors.rightMargin: Mycroft.Units.gridUnit * 2
        height: Mycroft.Units.gridUnit * 8

        Kirigami.Heading {
            id: viewTopAreaHeading
            level: 1
            text: networkName
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: Mycroft.Units.gridUnit * 3
            elide: Text.ElideRight
            maximumLineCount: 1
            color: Kirigami.Theme.textColor
            horizontalAlignment: Text.AlignHCenter
        }

        Item {
            id: viewTopIconCircleHolder
            anchors.top: viewTopAreaHeading.bottom
            anchors.topMargin: 4
            anchors.bottomMargin: 4
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: viewTopStatusLabel.top

            Rectangle {
                id: viewTopIconCircle
                radius: Mycroft.Units.gridUnit * 10
                color: Kirigami.Theme.highlightColor
                width: Mycroft.Units.gridUnit * 3
                height: Mycroft.Units.gridUnit * 3
                anchors.centerIn: parent

                Kirigami.Icon {
                    id: viewTopIcon
                    source: "network-wireless"
                    anchors.centerIn: parent
                    width: Mycroft.Units.gridUnit * 1.5
                    height: Mycroft.Units.gridUnit * 1.5
                }
            }
        }

        Label {
            id: viewTopStatusLabel
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            horizontalAlignment: Text.AlignHCenter
            color: Kirigami.Theme.textColor
            text: networkState
        }        
    }

    Flickable {
        id: viewMiddleArea
        anchors.top: viewTopArea.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: viewBottomArea.top
        anchors.topMargin: Mycroft.Units.gridUnit / 2
        anchors.bottomMargin: Mycroft.Units.gridUnit
        contentWidth: width
        contentHeight: viewMiddleAreaLayout.implicitHeight
        clip: true

        ColumnLayout {
            id: viewMiddleAreaLayout
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: Mycroft.Units.gridUnit * 2
            anchors.rightMargin: Mycroft.Units.gridUnit * 2
            anchors.topMargin: Mycroft.Units.gridUnit

            ViewPod {
                id: networkSpeedPod
                Layout.fillWidth: true
                Layout.preferredHeight: Mycroft.Units.gridUnit * 3
                podIcon: "speedometer"
                podMainText: "Network Speed"
                podSubText: networkSpeed
            }

            ViewPod {
                id: networkSecurityPod
                Layout.fillWidth: true
                Layout.preferredHeight: Mycroft.Units.gridUnit * 3
                podIcon: "lock"
                podMainText: "Security"
                podSubText: networkSecurity
            }

            ViewPod {
                id: ipAddressPod
                Layout.fillWidth: true
                Layout.preferredHeight: Mycroft.Units.gridUnit * 3
                podIcon: "network-connect"
                podMainText: "IP Address"
                podSubText: networkAddress
            }
        }
    }

    Item {
        id: viewBottomArea
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: Mycroft.Units.gridUnit * 5

        RowLayout {
            id: viewBottomAreaLayout
            anchors.fill: parent
            spacing: Mycroft.Units.gridUnit

            BottomActionButton {
                id: backButton
                Layout.fillWidth: true
                Layout.fillHeight: true
                buttonText: "Back"
                buttonIcon: "arrow-left"
                buttonAction: "ovos.phal.gui.network.client.internal.back"
            }

            BottomActionButton {
                id: forgetButton
                Layout.fillWidth: true
                Layout.fillHeight: true
                buttonText: "Forget"
                buttonIcon: "user-trash-symbolic"
                buttonAction: "ovos.phal.nm.forget"
                connectionName: manageConnectedNetworkView.networkName
            }
        }
    }
}
