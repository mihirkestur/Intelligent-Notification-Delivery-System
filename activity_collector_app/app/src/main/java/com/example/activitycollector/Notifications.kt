package com.example.activitycollector

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.net.http.UrlRequest.Status
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat


class Notifications: NotificationListenerService() {
     private fun startForeground() {
        val channel = NotificationChannel(
            "NOTIF_CHANNEL",
            "NOTIF_CHANNEL",
            NotificationManager.IMPORTANCE_HIGH
        )
        channel.description = "ActivityCollector channel for listening to notifications in foreground"
        val notificationManager =
             getSystemService<NotificationManager>(NotificationManager::class.java)
         notificationManager.createNotificationChannel(channel);

         val notification = NotificationCompat.Builder(this, "NOTIF_CHANNEL")
            // Create the notification to display while the service is running
            .build()
        ServiceCompat.startForeground(
            this,
            11001,
            notification,
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE,
)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        startForeground()
        return Service.START_STICKY
    }

    override fun onListenerConnected() {
        super.onListenerConnected()
        Log.d("Notifications", "notification listener connected")
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        Log.d("NotificationPosted", sbn.toString())
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        super.onNotificationRemoved(sbn)
    }

    override fun onNotificationRemoved (sbn: StatusBarNotification,
                                        rankingMap: RankingMap,
                                        reason: Int) {
        super.onNotificationRemoved(sbn, rankingMap, reason)
        Log.d("NotificationRemoved", sbn.toString())
        if (reason == REASON_CLICK) {
            Log.d("NotificationRemoved","clicked")
        } else if (reason == REASON_CANCEL) {
            Log.d("NotificationRemoved", "cancelled")
        } else {
            Log.d("NotificationRemoved", reason.toString())
        }
    }
}