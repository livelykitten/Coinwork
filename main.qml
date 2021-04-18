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
    Timer {
        interval: 50; running: true; repeat: true
        onTriggered: function () { monitor.update(); label.text = monitor.get() }
    }
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
                rotation: 180
                anchors {
                           top: parent.top // button.bottom
                           bottom: parent.bottom
                           left: parent.left
                           right: parent.right
                       }
                model: MsgModel {}
                delegate: MsgDelegate {}
            }

            Label {
                id: label
                text: monitor.get()
                font.pixelSize: 22
                // anchors.horizontalCenter: msgTab.horizontalCenter
            }
        }
        Item {
            id: alarmTab
        }
    }
}
