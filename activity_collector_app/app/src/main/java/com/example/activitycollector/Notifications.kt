package com.example.activitycollector

import android.annotation.SuppressLint
import android.app.Notification
import android.app.Service
import android.content.Intent
import android.content.pm.ServiceInfo
import android.location.Location
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log
import androidx.core.app.ServiceCompat
import com.google.android.gms.location.ActivityRecognition
import com.google.android.gms.location.ActivityRecognitionClient
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.asDeferred
import javax.inject.Inject

@AndroidEntryPoint
class Notifications : NotificationListenerService() {
    private lateinit var activityRecognitionClient: ActivityRecognitionClient
    private val job = SupervisorJob()
    private val lifecycleScope = CoroutineScope(Dispatchers.IO + job)
    private lateinit var fusedLocationClient: FusedLocationProviderClient
    @Inject
    lateinit var activityRepository: DataRepository

    private object Constants {
        const val TAG = "NOTIFICATION_LISTENER"
    }

    private fun startForeground() {
        Log.d(Constants.TAG, "created notification in ${Constants.TAG}");
        ServiceCompat.startForeground(
            this,
            NotificationCreator.notificationId(),
            NotificationCreator.notification(this),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE,
        )
    }

    override fun onCreate() {
        super.onCreate()
        NotificationCreator.initializeNotificationChannel(this)
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
        activityRecognitionClient = ActivityRecognition.getClient(this)
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
        if (sbn == null) {
            return
        }

        lifecycleScope.launch {
            Log.d(Constants.TAG, "[Notification Incoming] $sbn")
            val currentActivity = activityRepository.readActivity()
            val currentLocation = lastLocation.firstOrNull()
            val longitude = currentLocation?.longitude
            val latitude = currentLocation?.latitude

            val packageName = sbn.packageName;
            val title = sbn.notification.extras.getString(Notification.EXTRA_TITLE)
//            val content = sbn.notification.extras.getString(Notification.EXTRA_TEXT)
            Log.d(
                Constants.TAG,
                "Notification POSTED [$packageName] [$title], Activity: [$currentActivity], Location($longitude, $latitude)"
            )
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        super.onNotificationRemoved(sbn)
    }

    override fun onNotificationRemoved(
        sbn: StatusBarNotification,
        rankingMap: RankingMap,
        reason: Int
    ) {
        super.onNotificationRemoved(sbn, rankingMap, reason)

        lifecycleScope.launch {
            Log.d(Constants.TAG, "[Notification Incoming] $sbn")
            val currentActivity = activityRepository.readActivity()
            val packageName = sbn.packageName;
            val title = sbn.notification.extras.getString(Notification.EXTRA_TITLE)
//            val content = sbn.notification.extras.getString(Notification.EXTRA_TEXT)

            when (reason) {
                REASON_CLICK -> {
                    Log.d(
                        Constants.TAG,
                        "clicked [$packageName] [$title], Activity: [$currentActivity]"
                    )
                }

                REASON_CANCEL -> {
                    Log.d(
                        Constants.TAG,
                        "cancelled [$packageName] [$title], Activity: [$currentActivity]"
                    )
                }

                else -> {
                    Log.d(
                        Constants.TAG,
                        "$reason [$packageName] [$title], Activity: [$currentActivity]"
                    )
                }
            }
        }
    }

    @SuppressLint("MissingPermission")
    val lastLocation: Flow<Location> = flow {
        emit(fusedLocationClient.lastLocation.asDeferred().await())
    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
    }
}