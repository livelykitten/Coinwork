import QtQuick 2.13
import QtQuick.Window 2.13
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
//import QtMultimedia 5.15
import QtQml 2.15

ApplicationWindow {
    id: mainWindow
    width: 600
    height: 800
    visible: true
    title: qsTr("코인 감시자")

    header: TabBar {
        id: bar
        width: parent.width
        TabButton {
            id: msgButton
            text: qsTr("메세지함")
            onClicked: {
//                msgSound.stop()
                msgButtonHighlighter.stop()
                bar.currentIndex = 0
            }
        }
        TabButton {
            text: qsTr("알람 목록")
        }
    }
    StackLayout {
        id: mainStack
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
    MsgDialog {
        id: msgDialog
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
    }

    AlarmDialog {
        id: alarmDialog
        x: Math.round((parent.width - width) / 2)
        y: Math.round((parent.height - height) / 2)
        alarmModel: alarmList.model
    }
//    SoundEffect {
//        id: msgSound
//        source: "alarm.wav"
//        loops: SoundEffect.Infinite
//    }

    Timer {
        id: msgButtonHighlighter
        interval: 500; running: false; repeat: true
        onTriggered: {
            if (msgButton.down) {
                msgButton.down = false
            }
            else {
                msgButton.down = true
            }
        }
    }

    Timer {
        interval: 500; running: true; repeat: true
        onTriggered: {
            var message_raw = monitor.get_messages_str()
            if (message_raw === "")
                return
            var message_list = message_raw.split("$")
            var new_item = 0

            for (var i = 0; i < message_list.length; i++) {
                new_item = JSON.parse(message_list[i])
                for (var j = 0; j < msgList.model.count; j++) {
                    if (new_item.msg_timestamp >= msgList.model.get(j).msg_timestamp) {
                        msgList.model.insert(j, new_item)
                        break
                    }
                }
                msgList.model.append(new_item)
            }
            while (Date.now() / 1000 - msgList.model.get(msgList.model.count - 1).msg_timestamp >= 86400) {
                msgList.model.remove(msgList.model.count - 1)
            }

            if (!mainWindow.active) {
                msgDialog.recent_msg = message_list[0]
                msgDialog.new_msg_num = message_list.length
                msgDialog.open()
            }
            if (mainStack.currentIndex !== 0) {
//                msgSound.play()
                msgButtonHighlighter.start()
            }

            mainWindow.alert(0)
        }
    }
}
