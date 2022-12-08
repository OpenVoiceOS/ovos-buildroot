import QtQuick.Layouts 1.12
import QtQuick 2.12
import QtQuick.Controls 2.12
import org.kde.kirigami 2.10 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: mainLoaderView
    leftPadding: 0
    rightPadding: 0
    topPadding: 0
    bottomPadding: 0
    background: Rectangle {
        color: Kirigami.Theme.backgroundColor
        z: -1
    }

    property var pageToLoad: sessionData.state

    contentItem: Loader {
        id: rootLoader
    }

    onPageToLoadChanged: {
        console.log(sessionData.state)
        rootLoader.setSource(sessionData.state + ".qml")
    }
}

