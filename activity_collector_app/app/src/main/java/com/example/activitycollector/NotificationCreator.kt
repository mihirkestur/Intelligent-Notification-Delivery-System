package com.example.activitycollector

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.core.app.NotificationCompat

class NotificationCreator {
    private var notificationChannelId = "com.example.activitycollector.ACTIVITY_COLLECTOR_ID"
    private var notificationId = 1
    private var channelWasInitialized = false;
    private var notification: Notification? = null

    companion object {
        private const val TAG = "NOTIFICATION_CREATOR"
        private var instance = NotificationCreator()

        fun initializeNotificationChannel(context: Context) {
            if (!instance.channelWasInitialized) {
                instance.createNotificationChannel(context)
                instance.channelWasInitialized = true
                Log.d(this.TAG, "Notification channel was created")
            }
        }

        fun notificationId(): Int {
            return instance.notificationId
        }

        fun notification(context: Context): Notification {
            if (instance.notification == null) {
                this.initializeNotificationChannel(context)
                instance.notification = instance.createNotification(context)
                Log.d(this.TAG, "Notification was created")
            }

            return instance.notification!!
        }
    }

    private fun createNotificationChannel(context: Context) {
        val channel = NotificationChannel(
            this.notificationChannelId,
            "Activity Service Notification Channel",
            NotificationManager.IMPORTANCE_HIGH
        )
        channel.description =
            "ActivityCollector channel for listening to notifications in foreground"

        val notificationManager =
            context.getSystemService<NotificationManager>(NotificationManager::class.java)

        notificationManager.createNotificationChannel(channel);
    }

    private fun createNotification(context: Context): Notification {
        val notificationIntent = Intent(context, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            context, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(context, notificationChannelId)
            // Create the notification to display while the service is running
            .setWhen(System.currentTimeMillis())
            .setContentTitle("Activity Collector")
            .setContentText("Activity Collector is running")
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }
}