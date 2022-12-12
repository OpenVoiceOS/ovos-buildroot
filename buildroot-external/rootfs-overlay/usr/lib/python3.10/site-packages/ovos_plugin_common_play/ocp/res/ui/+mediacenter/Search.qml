/*
 *  Copyright 2018 by Aditya Mehra <aix.m@outlook.com>
 *  Copyright 2018 Marco Martin <mart@kde.org>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.

 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.

 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import QtQuick.Layouts 1.4
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Item {
    id: root
    property bool compactMode: height < 600 ? 1 : 0

    onFocusChanged: {
        if (focus) {
            txtFld.forceActiveFocus()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Mycroft.Units.gridUnit * 0.5

        Item {
            id: topAreaSearchPage
            Layout.fillWidth: true
            Layout.preferredHeight: compactMode ?  Mycroft.Units.gridUnit * 0.5 : Mycroft.Units.gridUnit * 3
        }

        Item {
            id: middleAreaSearchPage
            Layout.fillWidth: true
            Layout.preferredHeight: heads.height + sep.height + txtFld.height + answerButton.height
            Layout.alignment: Qt.AlignVCenter | Qt.AlignHCenter

            Rectangle {
                id: heads
                anchors.top: parent.top
                width: Mycroft.Units.gridUnit * 20
                height: compactMode ? Mycroft.Units.gridUnit * 3 :  Mycroft.Units.gridUnit * 4
                color: Kirigami.Theme.backgroundColor
                radius: Mycroft.Units.gridUnit * 0.5
                
                Label {
                    text: "Find Something To Play"                    
                    anchors.fill: parent
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight                   
                    wrapMode: Text.WordWrap
                    color: Kirigami.Theme.textColor
                    font.pixelSize: parent.height * 0.4
                }
            }

            Item {
                id: sep
                anchors.top: heads.bottom
                width: parent.width
                height: Kirigami.Units.largeSpacing
            }

            Rectangle {
                id: txtFld
                anchors.top: sep.bottom
                width: parent.width
                height: compactMode ? Kirigami.Units.gridUnit * 3 : Kirigami.Units.gridUnit * 5
                color: "transparent"
                border.width: 2
                radius: Mycroft.Units.gridUnit * 0.5
                border.color: txtFld.activeFocus ? Kirigami.Theme.linkColor : "transparent"
                KeyNavigation.down: answerButton
                focus: true

                Keys.onReturnPressed: {
                    txtFldInternal.forceActiveFocus()
                }

                TextField {
                    id: txtFldInternal
                    anchors.fill: parent
                    anchors.margins: Kirigami.Units.gridUnit / 3
                    KeyNavigation.down: answerButton
                    placeholderText: "Search for music, podcasts, movies ..."
                    font.pixelSize: parent.height * 0.3
                    font.bold: true

                    onAccepted: {
                        triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                    }
                    Keys.onReturnPressed: {
                        triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                    }
                }
            }

            Button {
                id: answerButton
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: txtFld.bottom
                anchors.margins: compactMode ? Mycroft.Units.gridUnit / 2 : Mycroft.Units.gridUnit
                height: compactMode ? Mycroft.Units.gridUnit * 3 : Mycroft.Units.gridUnit * 4
                KeyNavigation.up: txtFld
                KeyNavigation.down: homepageButtonTangle

                background: Rectangle {
                    id: answerButtonBackground
                    color: answerButton.activeFocus ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.highlightColor, 1.5)
                    radius: Mycroft.Units.gridUnit
                }

                SequentialAnimation {
                    id: answerButtonAnim

                    PropertyAnimation {
                        target: answerButtonBackground
                        property: "color"
                        to: Qt.lighter(Kirigami.Theme.highlightColor, 1.5)
                        duration: 200
                    }

                    PropertyAnimation {
                        target: answerButtonBackground
                        property: "color"
                        to: answerButton.activeFocus ? Kirigami.Theme.highlightColor : Qt.darker(Kirigami.Theme.highlightColor, 1.5)
                        duration: 200
                    }
                }

                contentItem: Item {
                    Kirigami.Heading {
                        anchors.centerIn: parent
                        text: "Play!"
                        level: compactMode ? 3 : 1
                    }
                }

                onClicked: {
                    triggerGuiEvent("search", { "utterance": txtFldInternal.text})
                }

                onPressed: {
                    answerButtonAnim.running = true;
                }

                Keys.onReturnPressed: {
                    clicked()
                }
            }
        }

        Item {
            id: bottomAreaSearchPage
            Layout.fillWidth: true            
            Layout.fillHeight: true
        }
    }
}