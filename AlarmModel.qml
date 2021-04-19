import QtQuick 2.0
import QtQml.Models 2.15

ListModel {
    id: alarmModel

    property var cid: 0

    ListElement {
        alarm_id: 0
        alarm_d_ratio: 0.1
        alarm_d_time: 900
        alarm_cooldown: 900
    }
}
