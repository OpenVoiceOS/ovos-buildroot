import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.ScrollableDelegate {
    id: delegateRoot
    skillBackgroundColorOverlay: "black"

    Component.onCompleted: {
        contentItem.ScrollBar.horizontal.policy = ScrollBar.AlwaysOff
    }

    Item {
        width: delegateRoot.width
        height: wolfImage.implicitHeight

        Image {
            id: wolfImage
            anchors.horizontalCenter: parent.horizontalCenter
            source: sessionData.wolfram_image
        }
    }
}