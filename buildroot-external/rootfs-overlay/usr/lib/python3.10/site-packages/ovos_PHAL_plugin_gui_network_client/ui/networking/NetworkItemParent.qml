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

Item {
    width: listView.width
    height: networkItemLayout.height

    readonly property Flickable listView: {
        var candidate = parent;
        while (candidate) {
            if (candidate instanceof Flickable) {
                return candidate;
            }
            candidate = candidate.parent;
        }
        return null;
    }

    RowLayout {
        id: networkItemLayout
        spacing: 0
        anchors.left: parent.left
        anchors.right: parent.right
        height: networkItemMain.height

        NetworkItem {
            id: networkItemMain            
            Layout.preferredWidth: parent.width * 0.90
        }

        Kirigami.Separator {
            Layout.alignment: Qt.AlignRight
            Layout.preferredWidth: 1
            Layout.fillHeight: true
        }

        NetworkItemSetting {
            Layout.preferredWidth: parent.width * 0.10
            Layout.fillHeight: true
            visible: model.ConnectionState == PlasmaNM.Enums.Activated || (model.ConnectionState == PlasmaNM.Enums.Deactivated && model.ConnectionPath)
        }
    }
}