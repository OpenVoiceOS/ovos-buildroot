/*
 * Copyright 2018 by Marco Martin <mart@kde.org>
 * Copyright 2018 David Edmundson <davidedmundson@kde.org>
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

import QtQuick 2.9
import QtGraphicalEffects 1.0
import org.kde.kirigami 2.5 as Kirigami
import Mycroft 1.0 as Mycroft

Item {
    id: root
    implicitWidth: Kirigami.Units.gridUnit * 5
    implicitHeight: width
    property var circleBackgroundColor: "#F5F5F5"
    property var circleInnerColor: "#CD5C5C"
    
    property bool hasShadow: true

    state: "idle"
    states: [
        State {
            name: "idle"
            PropertyChanges {
                target: innerCircle
                graphicsColor: circleInnerColor
                backgroundColor: circleBackgroundColor
            }
            PropertyChanges {
                target: root
                opacity: 0
            }
            StateChangeScript {
                script: {
                    innerCircleRotation.running = false;
                    innerCircleRotation.to = 0;
                    innerCircleRotation.loops = 1;
                    innerCircleRotation.running = true;

                    outerCircleRotation.loops = 1;
                    outerCircleRotation.restart();

                    fadeTimer.running = false;
                }
            }
        },
        State {
            name: "waiting"
            PropertyChanges {
                target: innerCircle
                graphicsColor: circleInnerColor
                backgroundColor: circleBackgroundColor
            }
            PropertyChanges {
                target: root
                opacity: 1
            }
            StateChangeScript {
                script: {
                    innerCircleRotation.running = false;
                    innerCircleRotation.to = -360;
                    innerCircleRotation.loops = 1;
                    innerCircleRotation.running = true;

                    outerCircleRotation.loops = 1;
                    outerCircleRotation.restart();

                    fadeTimer.running = false;
                }
            }
        },
        State {
            name: "loading"
            PropertyChanges {
                target: innerCircle
                targetRotation: 0
                graphicsColor: circleInnerColor
                backgroundColor: circleBackgroundColor
            }
            PropertyChanges {
                target: root
                opacity: 1
            }

            StateChangeScript {
                script: {
                    innerCircleRotation.running = false;
                    innerCircleRotation.to = innerCircle.rotation - 360;
                    innerCircleRotation.loops = Animation.Infinite;
                    innerCircleRotation.running = true;

                    outerCircleRotation.loops = Animation.Infinite;
                    outerCircleRotation.restart();

                    fadeTimer.running = false;
                }
            }
        },
        State {
            name: "ok"
            PropertyChanges {
                target: innerCircle
                explicit: true
                targetRotation: -90
                graphicsColor: Kirigami.Theme.positiveTextColor
                backgroundColor: Qt.tint(Kirigami.Theme.backgroundColor, Qt.rgba(Kirigami.Theme.positiveTextColor.r, Kirigami.Theme.positiveTextColor.g, Kirigami.Theme.positiveTextColor.b, 0.4))
            }
            PropertyChanges {
                target: root
                opacity: 1
            }
            StateChangeScript {
                script: {
                    innerCircleRotation.running = false;
                    innerCircleRotation.to = -90;
                    innerCircleRotation.loops = 1;
                    innerCircleRotation.running = true;

                    outerCircleRotation.loops = 1;
                    outerCircleRotation.restart();

                    fadeTimer.restart();
                }
            }
        },
        State {
            name: "error"
            PropertyChanges {
                target: innerCircle
                explicit: true
                graphicsColor: "white"
                backgroundColor: Qt.tint(Kirigami.Theme.backgroundColor, Qt.rgba(Kirigami.Theme.negativeTextColor.r, Kirigami.Theme.negativeTextColor.g, Kirigami.Theme.negativeTextColor.b, 0.4))
            }
            PropertyChanges {
                target: root
                opacity: 1
            }
            StateChangeScript {
                script: {
                    innerCircleRotation.running = false;
                    innerCircleRotation.to = 90;
                    innerCircleRotation.loops = 1;
                    innerCircleRotation.running = true;

                    outerCircleRotation.loops = 1;
                    outerCircleRotation.restart();

                    fadeTimer.restart();
                }
            }
        }
    ]

    Connections {
        target: Mycroft.MycroftController
        onListeningChanged: {
            if (Mycroft.MycroftController.listening) {
                root.state = "waiting";
            } else {
                fadeTimer.restart();
            }
        }
        onNotUnderstood: {
            root.state = "idle"
            root.state = "error";
        }
        onFallbackTextRecieved: {
            if (skill.length > 0) {
                root.state = "ok";
            }
        }
        onServerReadyChanged: {
            if (Mycroft.MycroftController.serverReady) {
                root.state = "ok";
            }
        }
        onStatusChanged: {
            switch (Mycroft.MycroftController.status) {
            case Mycroft.MycroftController.Open:
                root.state = Mycroft.MycroftController.serverReady ? "ok" : "loading";
                break;
            case Mycroft.MycroftController.Connecting:
                root.state = "loading";
                break;
            case Mycroft.MycroftController.Error:
            default:
                root.state = "error";
                break;
            }
        }
        onCurrentIntentChanged: {
            if (Mycroft.MycroftController.currentIntent.length == 0) {
                if (root.state == "loading") {
                    root.state = "idle";
                }
            } else {
                root.state = "loading";
            }
        }
    }

    Rectangle {
        id: background
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height)
        height: width
        color: innerCircle.backgroundColor
        radius: height
        layer.enabled: hasShadow
        layer.effect: DropShadow {
            cached: true
            transparentBorder: true
            horizontalOffset: 0
            verticalOffset: 2
        }
    }
    Behavior on opacity {
        OpacityAnimator {
            duration: innerCircle.animationLength
            easing.type: Easing.InOutCubic
        }
    }

    Rectangle {
        id: innerCircleGraphics
        anchors {
            fill: outerCircle
            margins: innerCircle.unit * 5
        }
        visible: false

        color: innerCircle.graphicsColor
        radius: width
    }
    Item {
        id: innerCircleMask
        visible: false
        anchors.fill: innerCircleGraphics

        Rectangle {
            anchors {
                left: parent.left
                right: parent.horizontalCenter
                top: parent.top
                bottom: parent.bottom
            }
            color: "white"
        }
    }
    OpacityMask {
        id: innerCircle
        property int unit: Math.max(1, background.width/20)
        property color graphicsColor
        property color backgroundColor
        property int animationLength: 1000
        property int targetRotation: 0
        Behavior on graphicsColor {
            ColorAnimation {
                duration: innerCircle.animationLength
                easing.type: Easing.InOutCubic
            }
        }
        Behavior on backgroundColor {
            ColorAnimation {
                duration: innerCircle.animationLength
                easing.type: Easing.InOutCubic
            }
        }
        anchors.fill: innerCircleGraphics
        source: innerCircleGraphics
        maskSource: innerCircleMask

        RotationAnimator {
            id: innerCircleRotation
            target: innerCircle
            from: innerCircle.rotation
            to: 0
            direction: RotationAnimator.Counterclockwise
            duration: innerCircle.animationLength
            easing.type: Easing.InOutCubic
        }
    }

    Item {
        id: outerCircle

        anchors {
            fill: background
            margins: innerCircle.unit * 3
        }

        // the little dot
        Rectangle {
            width: innerCircle.unit * 2
            height: width
            radius: width
            color: innerCircle.graphicsColor
            anchors.horizontalCenter : parent.horizontalCenter
        }
        //the circle
        Rectangle {
            anchors {
                fill: parent
                margins: innerCircle.unit * 3
            }
            radius: width
            color: "transparent"
            border.width: innerCircle.unit 
            border.color: innerCircle.graphicsColor
        }
        RotationAnimator {
            id: outerCircleRotation
            target: outerCircle
            from: outerCircle.rotation
            to: outerCircle.rotation + 360 - (outerCircle.rotation + 360) % 360
            direction: RotationAnimator.Clockwise
            duration: innerCircle.animationLength
            easing.type: Easing.InOutCubic
        }
    }
    Timer {
        id: fadeTimer
        interval: 3000
        repeat: false
        onTriggered: root.state = "idle"
    }
}
