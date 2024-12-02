package com.example.activitycollector

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationManager
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
import com.google.firebase.Firebase
import com.google.firebase.firestore.firestore
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch
import kotlinx.coroutines.tasks.asDeferred
import java.time.Instant
import java.time.ZoneId
import java.time.ZonedDateTime
import java.time.temporal.ChronoField
import javax.inject.Inject
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sqrt
import kotlin.time.Duration

data class LocationRepr(val long: Double, val lat: Double, val radius: Double?) {
    constructor(long: Double, lat: Double) : this(long, lat, null)
}

@AndroidEntryPoint
class Notifications : NotificationListenerService() {
    private lateinit var activityRecognitionClient: ActivityRecognitionClient
    private val job = SupervisorJob()
    private val lifecycleScope = CoroutineScope(Dispatchers.IO + job)
    private lateinit var fusedLocationClient: FusedLocationProviderClient

    @Inject
    lateinit var activityRepository: DataRepository

    private val db = Firebase.firestore

    private object Constants {
        const val TAG = "NOTIFICATION_LISTENER"
        val KNOWN_LOCATIONS = hashMapOf(
            "HOME" to LocationRepr(
                -73.11006,
                40.90665,
                0.03, // kilometres
            ),
            "LIBRARY" to LocationRepr(
                -73.11496,
                40.91006,
                0.34,
            ),
            "UNIVERSITY" to LocationRepr(
                -73.12731,
                40.91634,
                0.89,
            )
        )
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
            val content = sbn.notification.extras.getString(Notification.EXTRA_TEXT)
            Log.d(
                Constants.TAG,
                "Notification POSTED [$packageName] [$title], Activity: [$currentActivity], Location($longitude, $latitude, ${
                    locationToReadable(
                        longitude,
                        latitude
                    )
                })"
            )

            val id = sbn.key + sbn.postTime

            val numberOfActiveNotifications = getActiveNotifications().size
            val timePosted = Instant.ofEpochMilli(sbn.postTime)
            val localDate = timePosted.atZone(ZoneId.systemDefault())

            val postedTimeObj = hashMapOf(
                "epoch_time" to sbn.postTime,
                "day" to localDate.toLocalDateTime().dayOfWeek.value,
                "normalized" to localDate.toLocalDateTime().get(ChronoField.SECOND_OF_DAY)
                    .toDouble() / 86400
            )

            val data = hashMapOf(
                "id" to id,
                "app_name" to packageName,
                "notification_title" to title,
                "notification_content" to content,
                "posted_time" to postedTimeObj,
                "posted_active_notifications" to numberOfActiveNotifications,
            )

            if (!(packageName.lowercase().contains("whatsapp") or
                        packageName.lowercase().contains("com.google.android.gm") or
                        packageName.lowercase().contains("com.instagram.android")
                        )
            ) {
                return@launch
            }

            db.collection("notifications")
                .add(data)
                .addOnSuccessListener { documentReference ->
                    Log.d(Constants.TAG, "DocumentSnapshot added with ID: ${documentReference.id}")
                }
                .addOnFailureListener { e ->
                    Log.w(Constants.TAG, "error adding document", e)
                }
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
            Log.d(Constants.TAG, "[Notification Removed] $sbn")
            val currentActivity = activityRepository.readActivity()
            val packageName = sbn.packageName;
            val title = sbn.notification.extras.getString(Notification.EXTRA_TITLE)
            val currentLocation = lastLocation.firstOrNull()
            val longitude = currentLocation?.longitude
            val latitude = currentLocation?.latitude

            if (!(packageName.lowercase().contains("whatsapp") or
                        packageName.lowercase().contains("com.google.android.gm")
                        or packageName.lowercase().contains("com.instagram.android")
                        )
            ) {
                Log.d(
                    Constants.TAG,
                    "clicked irrelevant package: [$packageName] [$title], Activity: [$currentActivity], Location($longitude, $latitude, ${
                        locationToReadable(
                            longitude,
                            latitude
                        )
                    })"
                )
                return@launch
            }

            val id = sbn.key + sbn.postTime
            val numberOfActiveNotifications = getActiveNotifications().size
            val timeRemoved = System.currentTimeMillis()
            val instant = Instant.ofEpochMilli(timeRemoved)
            val zoneDate = instant.atZone(ZoneId.systemDefault()).toLocalDateTime()

            val removedTimeObj = hashMapOf(
                "epoch_time" to timeRemoved,
                "day" to zoneDate.dayOfWeek.value,
                "normalized" to zoneDate.get(ChronoField.SECOND_OF_DAY).toDouble() / 86400
            )

            val reasonString = "not_sure"
            // Whatsapp -> 8 is click, 12 is delete
            // Gmail -> 24 is click
            when (reason) {
                REASON_CLICK -> {
                    Log.d(
                        Constants.TAG,
                        "clicked [$packageName] [$title], Activity: [$currentActivity], Location: ${
                            locationToReadable(
                                longitude,
                                latitude
                            )
                        }"
                    )
                }

                REASON_CANCEL -> {
                    Log.d(
                        Constants.TAG,
                        "cancelled [$packageName] [$title], Activity: [$currentActivity], Location: ${
                            locationToReadable(
                                longitude,
                                latitude
                            )
                        }"
                    )
                }

                REASON_APP_CANCEL -> {
                    Log.d(
                        Constants.TAG,
                        "whatsapp click [$packageName] [$title], Activity: [$currentActivity]"
                    )
                }

                else -> {
                    Log.d(
                        Constants.TAG,
                        "$reason [$packageName] [$title], Activity: [$currentActivity]"
                    )
                }
            }

//            val data = hashMapOf(
//                "activity" to currentActivity,
//                "location_longitude" to longitude,
//                "location_latitude" to latitude,
//                "app_name" to packageName,
//                "notification_title" to title,
//                "posted_time" to sbn.postTime,
//                "interaction_time" to System.currentTimeMillis(),
//                "reason_number" to reason,
//            )

            val query = db.collection("notifications").whereEqualTo("id", id)
            query.get()
                .addOnSuccessListener { querySnapShot ->
                    if (!querySnapShot.isEmpty) {
                        Log.d(Constants.TAG, "found object")
                        val document = querySnapShot.documents[0]
                        val location = hashMapOf(
                            "long" to longitude,
                            "lat" to latitude,
                            "readable" to locationToReadable(longitude, latitude),
                        )

                        val updates = hashMapOf(
                            "activity" to currentActivity,
                            "location" to location,
                            "interaction_time" to removedTimeObj,
                            "interaction_active_notifications" to numberOfActiveNotifications,
                            "reason_number" to reason,
                        )

                        Log.d(Constants.TAG, "attempting update $updates")

                        document.reference.update(updates)
                            .addOnSuccessListener {
                                Log.d(
                                    Constants.TAG,
                                    "success updating ${document.data} with $updates"
                                )
                            }
                            .addOnFailureListener { e ->
                                Log.e(Constants.TAG, "failed to update ${document.data}")
                            }
                    } else {
                        Log.e(Constants.TAG, "matching notification not found: $id")
                        val content = sbn.notification.extras.getString(Notification.EXTRA_TEXT)
                        val timePosted = Instant.ofEpochMilli(sbn.postTime)
                        val localDate = timePosted.atZone(ZoneId.systemDefault())
                        val postedTimeObj = hashMapOf(
                            "epoch_time" to sbn.postTime,
                            "day" to localDate.toLocalDateTime().dayOfWeek.value,
                            "normalized" to localDate.toLocalDateTime().get(ChronoField.SECOND_OF_DAY)
                                .toDouble() / 86400
                        )

                        val location = hashMapOf(
                            "long" to longitude,
                            "lat" to latitude,
                            "readable" to locationToReadable(longitude, latitude),
                        )

                        val data = hashMapOf(
                            "id" to id,
                            "app_name" to packageName,
                            "notification_title" to title,
                            "notification_content" to content,
                            "posted_time" to postedTimeObj,
                            "posted_active_notifications" to numberOfActiveNotifications,
                            "activity" to currentActivity,
                            "location" to location,
                            "interaction_time" to removedTimeObj,
                            "interaction_active_notifications" to numberOfActiveNotifications,
                            "reason_number" to reason,
                        )

                        db.collection("notifications").add(data)
                    }
                }
                .addOnFailureListener { e ->
                    Log.e(Constants.TAG, "failed to query id: $id, error: $e")
                }

//            db.collection("notifications")
//                .add(data)
//                .addOnSuccessListener { documentReference ->
//                    Log.d(Constants.TAG, "DocumentSnapshot added with ID: ${documentReference.id}")
//                }
//                .addOnFailureListener{ e ->
//                    Log.w(Constants.TAG, "error adding document", e)
//                }
        }
    }

    @SuppressLint("MissingPermission")
    val lastLocation: Flow<Location> = flow {
        emit(fusedLocationClient.lastLocation.asDeferred().await())
    }

    private fun locationToReadable(long: Double?, lat: Double?): String {
        val longSafe = long ?: 0.0
        val latSafe = lat ?: 0.0

        for (entry in Constants.KNOWN_LOCATIONS) {
            if (arePointsNear(longSafe, latSafe, entry.value)) {
                return entry.key
            }
        }
        return "UNKNOWN"
    }

    private fun arePointsNear(
        checkPointLong: Double,
        checkPointLat: Double,
        centerPoint: LocationRepr
    ): Boolean {
        val ky = 40000 / 360;
        val kx = cos(Math.PI * centerPoint.long / 180.0) * ky;
        val dx = abs(centerPoint.long - checkPointLong) * kx;
        val dy = abs(centerPoint.lat - checkPointLat) * ky;
        return sqrt(dx * dx + dy * dy) <= centerPoint.radius!!;
    }

    override fun onDestroy() {
        super.onDestroy()
        job.cancel()
    }
}