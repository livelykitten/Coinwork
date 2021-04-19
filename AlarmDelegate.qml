import QtQuick 2.0
import QtQuick.Controls 2.15

import QtQuick 2.11
import QtQuick.Controls 2.4
import QtQuick.Controls.Material 2.4
import QtQuick.Layouts 1.11
import QtQuick.Window 2.11

ItemDelegate {
    id: root
    width: ListView.view.width
    anchors.leftMargin: 100
    anchors.rightMargin: 100
    contentItem: ColumnLayout {
        Label {
            text: "Alarm #" + model.alarm_id.toString()
        }
        Label {
            text: "d_ratio: " + (model.alarm_d_ratio * 100).toString() + "%"
        }
        Label {
            text: "d_time: " + Math.floor(model.alarm_d_time / 60).toString() + " min " + (model.alarm_d_time % 60).toString() + " sec"
        }
        Label {
            text: "cooldown: " + (model.alarm_cooldown / 60).toString() + " min "
        }
    }
}
