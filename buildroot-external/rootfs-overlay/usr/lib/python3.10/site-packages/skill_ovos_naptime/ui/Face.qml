import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    id: root

    property bool eyesOpen
    property string mouth
    property alias mouthItem: mouthItem

    Item {
        id: fixedProportionsContainer

        anchors.centerIn: parent
        readonly property real proportion: 1.6

        width: parent.height / parent.width >= proportion ? parent.width : height / 1.6
        height: parent.height / parent.width >= proportion ? width * 1.6 : parent.height

        Item {
            anchors {
                left: parent.left
                top: parent.top
                topMargin: parent.height * 0.28
                leftMargin: parent.width * 0.02
            }

            width: parent.width * 0.35
            height: width
            Image {
                anchors.fill: parent
                visible: root.eyesOpen
                source: Qt.resolvedUrl("face/Eyeball.svg")
                fillMode: Image.PreserveAspectFit
            }
            Image {
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                    leftMargin: width * 0.001
                    rightMargin: width * 0.001
                }
                height: width / (sourceSize.width/sourceSize.height)
                visible: !root.eyesOpen
                source: Qt.resolvedUrl("face/lid.svg")
                fillMode: Image.PreserveAspectFit
            }
            Image {
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    leftMargin: width * 0.001
                    rightMargin: width * 0.001
                }
                height: width / (sourceSize.width/sourceSize.height)
                visible: root.eyesOpen
                source: Qt.resolvedUrl("face/upper-lid.svg")
                fillMode: Image.PreserveAspectFit
            }
        }

        Item {
            anchors {
                right: parent.right
                top: parent.top
                topMargin: parent.height * 0.28
                rightMargin: parent.width * 0.02
            }

            width: parent.width * 0.35
            height: width
            Image {
                anchors.fill: parent
                visible: root.eyesOpen
                source: Qt.resolvedUrl("face/Eyeball.svg")
                fillMode: Image.PreserveAspectFit
            }
            Image {
                anchors {
                    left: parent.left
                    right: parent.right
                    bottom: parent.bottom
                    leftMargin: width * 0.001
                    rightMargin: width * 0.001
                }
                height: width / (sourceSize.width/sourceSize.height)
                visible: !root.eyesOpen
                source: Qt.resolvedUrl("face/lid.svg")
                fillMode: Image.PreserveAspectFit
            }
            Image {
                anchors {
                    left: parent.left
                    right: parent.right
                    top: parent.top
                    leftMargin: width * 0.001
                    rightMargin: width * 0.001
                }
                height: width / (sourceSize.width/sourceSize.height)
                visible: root.eyesOpen
                source: Qt.resolvedUrl("face/upper-lid.svg")
                fillMode: Image.PreserveAspectFit
            }
        }

        Item {
            id: mouthItem
            anchors {
                horizontalCenter: parent.horizontalCenter
                bottom: parent.bottom
                bottomMargin: parent.height * 0.26
            }
            width: parent.width / 2
            height: smile.implicitHeight
            Image {
                id: smile
                anchors {
                    left: parent.left
                    right: parent.right
                    verticalCenter: parent.verticalCenter
                }
                fillMode: Image.PreserveAspectFit
                source: Qt.resolvedUrl("face/" + root.mouth)
            }
        }
    }
}
