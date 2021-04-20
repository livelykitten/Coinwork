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
    contentItem: RowLayout {
        ColumnLayout {
            Label {
                text: "알람 번호 #" + model.alarm_id.toString()
            }
            Label {
                text: "변동 비율: " + (model.alarm_d_ratio * 100).toString() + "%"
            }
            Label {
                text: "시간 간격: " + Math.floor(model.alarm_d_time / 60).toString() + " 분 " + (model.alarm_d_time % 60).toString() + " 초"
            }
            Label {
                text: "알림 주기: " + (model.alarm_cooldown / 60).toString() + " 분"
            }
        }
        Item {
            Layout.fillWidth: true
        }

        Button {
            text: "삭제"
            onClicked: {
                if (model.alarm_id !== 0) {
                    console.log(monitor.remove_criteria(model.alarm_id))
                }
                root.ListView.view.model.remove(index)
            }
        }
    }
}
