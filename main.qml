import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml 2.15

ApplicationWindow {
    width: 480
    height: 640
    visible: true
    title: qsTr("Hello World")

    header: TabBar {
        id: bar
        width: parent.width
        TabButton {
            text: qsTr("Messages")
        }
        TabButton {
            text: qsTr("Alarms")
        }
    }
    StackLayout {
        width: parent.width
        currentIndex: bar.currentIndex
        anchors.fill: parent
        Item {
            id: msgTab
            ListView {
                id: msgList
                anchors {
                           top: parent.top // button.bottom
                           bottom: parent.bottom
                           left: parent.left
                           right: parent.right
                       }
                model: MsgModel {}
                delegate: MsgDelegate {}
            }
        }
        Item {
            id: alarmTab
            ListView {
                id: alarmList
                anchors {
                           top: parent.top // button.bottom
                           bottom: parent.bottom
                           left: parent.left
                           right: parent.right
                       }
                model: AlarmModel {}
                delegate: AlarmDelegate {}
            }
            RoundButton {
                id: addAlarmButton
                text: "+"
                anchors.bottom: alarmList.bottom
                anchors.bottomMargin: 8
                anchors.horizontalCenter: parent.horizontalCenter
                onClicked: alarmDialog.open()
            }
        }
    }
    AlarmDialog {
        id: alarmDialog
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        alarmModel: alarmList.model
    }
    Timer {
        interval: 500; running: true; repeat: true
        onTriggered: function () {
            monitor.monitor();
            if (monitor.message_left()) {
            }
            while (monitor.message_left()) {
                msgList.model.add_item_sorted(JSON.parse(monitor.get_message()))
            }
        }
    }
}
