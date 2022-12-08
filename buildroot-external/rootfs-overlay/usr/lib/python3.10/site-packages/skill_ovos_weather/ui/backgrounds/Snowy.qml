import QtQuick 2.4
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.2
import QtQuick.Shapes 1.12
import org.kde.kirigami 2.11 as Kirigami
import "components"

Rectangle {
    property bool inView: visible
    color: "transparent"

    Snow {
        anchors.fill: parent
        inView: parent.inView
    }
}

