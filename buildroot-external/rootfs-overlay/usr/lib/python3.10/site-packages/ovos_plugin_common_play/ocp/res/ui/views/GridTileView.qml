/*
 *  Copyright 2019 Aditya Mehra <aix.m@outlook.com>
 *  Copyright 2019 Marco Martin <mart@kde.org>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  2.010-1301, USA.
 */

import QtQuick 2.9
import QtQuick.Layouts 1.4
import QtQuick.Controls 2.4 as Controls
import org.kde.kirigami 2.5 as Kirigami

FocusScope {
    id: root
        
    signal activated
    property string title
    property alias view: view
    property alias delegate: view.delegate
    property alias model: view.model
    property alias count: view.count
    property alias currentIndex: view.currentIndex
    property alias currentItem: view.currentItem
    Layout.fillWidth: true
    implicitHeight: view.implicitHeight + header.implicitHeight
    property alias cellWidth: view.cellWidth
    property alias cellHeight: view.cellHeight
    
    property Item navigationUp
    property Item navigationDown

    Kirigami.Heading {
        id: header
        anchors {
            left: parent.left
            right: parent.right
            top: parent.top
            leftMargin: Kirigami.Units.largeSpacing * 3
        }
        text: title
        color: "white"
    }

    Kirigami.Separator {
        z: 2
        anchors {
            bottom: view.top
            left: view.left
            right: parent.right
        }
        height: 1
        color: "white"
        opacity: 0.4
        visible: view.contentY > 0
    }

    GridView {
        id: view
        anchors {
                left: parent.left
                right: parent.right
                top: header.bottom
                bottom: parent.bottom
                topMargin: Kirigami.Units.largeSpacing * 2
                leftMargin: Kirigami.Units.largeSpacing * 2
                rightMargin: Kirigami.Units.largeSpacing * 2
        }
        focus: true
        z: activeFocus ? 10: 1 
        cellWidth: parent.width / 4
        cellHeight: parent.height / 1.5
        keyNavigationEnabled: true
        highlightFollowsCurrentItem: true
        snapMode: ListView.SnapToItem
        cacheBuffer: width
        highlightMoveDuration: Kirigami.Units.longDuration
        clip: true
        
        onCurrentItemChanged: {
            positionViewAtIndex(currentIndex, GridView.Center)
        }
        
        move: Transition {
            SmoothedAnimation {
                property: "x"
                duration: Kirigami.Units.longDuration
            }
        }

        KeyNavigation.left: root
        KeyNavigation.right: root
    }
}
