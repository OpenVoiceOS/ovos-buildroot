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
    id: networkSelectionView

    Kirigami.Theme.inherit: false
    Kirigami.Theme.colorSet: Kirigami.Theme.Complementary
    color: Kirigami.Theme.backgroundColor

    property string pathToRemove
    property string nameToRemove
    property bool isStartUp: false
    
    function removeConnection(nameToRemove) {
        Mycroft.MycroftController.sendRequest("ovos.phal.nm.forget", {"connection_name": nameToRemove})
    }

    PlasmaNM.NetworkStatus {
        id: networkStatus
    }

    PlasmaNM.ConnectionIcon {
        id: connectionIconProvider
    }

    PlasmaNM.Handler {
        id: handler
    }

    PlasmaNM.AvailableDevices {
        id: availableDevices
    }

    PlasmaNM.NetworkModel {
        id: connectionModel
    }

    PlasmaNM.AppletProxyModel {
        id: appletProxyModel
        sourceModel: connectionModel
    }

    PlasmaCore.ColorScope {
        anchors.fill: parent
        colorGroup: PlasmaCore.Theme.ComplementaryColorGroup
        Kirigami.Theme.colorSet: Kirigami.Theme.Complementary

        ColumnLayout {
            spacing: 0
            anchors {
                fill: parent
                margins: Kirigami.Units.largeSpacing
            }


            Kirigami.Heading {
                id: connectionTextHeading
                level: 1
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.bold: true
                text: i18n("Select Your Wi-Fi")
                color: Kirigami.Theme.highlightColor
            }
            Item {
                Layout.preferredHeight: Kirigami.Units.largeSpacing
            }

            Kirigami.Separator {
                Layout.preferredHeight: 1
                Layout.fillWidth: true
            }

            Kirigami.ScrollablePage {
                id: page
                supportsRefreshing: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                onRefreshingChanged: {
                    if (refreshing) {
                        refreshTimer.restart()
                        handler.requestScan();
                    }
                }
                Timer {
                    id: refreshTimer
                    interval: 3000
                    onTriggered: page.refreshing = false
                }

                ListView {
                    id: connectionView

                    model: appletProxyModel
                    currentIndex: -1
                    //boundsBehavior: Flickable.StopAtBounds
                    delegate: NetworkItemParent{}
                }
            }

            Kirigami.Separator {
                Layout.preferredHeight: 1
                Layout.fillWidth: true
            }

            Item {
                Layout.preferredHeight: Kirigami.Units.largeSpacing
            }

            RowLayout {
                Kirigami.BasicListItem {
                    Layout.fillWidth: false
                    separatorVisible: false
                    visible: true
                    icon: "go-previous-symbolic"
                    text: i18n("Back")
                    Layout.preferredWidth: implicitWidth + height
                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("../sounds/ui_sounds_clicked.wav"))
                        networkingLoader.clear()
                        Mycroft.MycroftController.sendRequest("ovos.phal.gui.network.client.back", {})
                    }
                }
                Item {
                    Layout.fillWidth: true
                }
                Kirigami.BasicListItem {
                    Layout.fillWidth: false
                    separatorVisible: false
                    icon: "view-refresh"
                    text: i18n("Refresh")
                    Layout.preferredWidth: implicitWidth + height
                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("../sounds/ui_sounds_clicked.wav"))
                        page.refreshing = true;
                        connectionView.contentY = -Kirigami.Units.gridUnit * 4;
                    }
                }
            }
        }
    }

    Control {
        id: passwordLayer
        anchors.fill: parent
        z: 999999
        opacity: 0
        enabled: opacity > 0
        leftPadding: Kirigami.Units.gridUnit
        rightPadding: Kirigami.Units.gridUnit
        property alias password: passField.text
        property var networkName
        property var securityType
        
        function open() {
            passField.text = "";
            passField.forceActiveFocus();
            opacity = 1;
        }

        function close() {
            opacity = 0;
            passField.text = "";
        }

        Behavior on opacity {
            OpacityAnimator {
                duration: Kirigami.Units.longDuration
                easing.type: Easing.InOutQuad
            }
        }

        background: Rectangle {
            color: Qt.rgba(0, 0, 0, 0.95)
        }

        contentItem: ColumnLayout {
            implicitWidth: Kirigami.Units.gridUnit * 25
            spacing: Kirigami.Units.gridUnit

            Kirigami.Heading {
                level: 2
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                font.bold: true
                text: i18n("Enter Password For %1", connectionName)
                color: Kirigami.Theme.highlightColor
            }

            Kirigami.PasswordField {
                id: passField
                Kirigami.Theme.colorSet: Kirigami.Theme.View
                Layout.fillWidth: true
                Layout.leftMargin: Mycroft.Units.gridUnit * 5
                Layout.rightMargin: Mycroft.Units.gridUnit * 5
                Layout.preferredHeight: Mycroft.Units.gridUnit * 4
                placeholderText: i18n("Password...")

                validator: RegExpValidator {
                    regExp: if (securityType == PlasmaNM.Enums.StaticWep) {
                                /^(?:.{5}|[0-9a-fA-F]{10}|.{13}|[0-9a-fA-F]{26}){1}$/
                            } else {
                                /^(?:.{8,64}){1}$/
                            }
                }

                onAccepted: {
                    networkingLoader.push(Qt.resolvedUrl("Connecting.qml"))
                    Mycroft.MycroftController.sendRequest("ovos.phal.nm.connect", {
                        "connection_name": passwordLayer.networkName,
                        "password": passwordLayer.password,
                        "security_type": passwordLayer.securityType
                    })
                    passwordLayer.close();
                }
            }

            RowLayout {
                Layout.alignment: Qt.AlignCenter
                Button {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Mycroft.Units.gridUnit * 5
                    text: i18n("Connect")
                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("../sounds/ui_sounds_clicked.wav"))
                        passField.accepted();
                    }
                }

                Button {
                    Layout.fillWidth: true                    
                    Layout.preferredHeight: Mycroft.Units.gridUnit * 5
                    text: i18n("Cancel")
                    onClicked: {
                        Mycroft.SoundEffects.playClickedSound(Qt.resolvedUrl("../sounds/ui_sounds_clicked.wav"))
                        passwordLayer.close();
                    }
                }
            }
            Item {
                Layout.fillHeight: true
            }
        }
    }
}
