package com.example.activitycollector

import android.Manifest
import android.app.PendingIntent
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.IBinder
import android.util.Log
import androidx.core.app.ActivityCompat
import androidx.core.app.ServiceCompat
import com.google.android.gms.location.ActivityRecognition
import com.google.android.gms.location.ActivityRecognitionClient
import com.google.android.gms.location.ActivityRecognitionResult
import com.google.android.gms.location.ActivityTransition
import com.google.android.gms.location.ActivityTransitionRequest
import com.google.android.gms.location.ActivityTransitionResult
import com.google.android.gms.location.DetectedActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import javax.inject.Inject
@AndroidEntryPoint
class ActivityDetectionService : Service() {
    private val job = SupervisorJob()
    private val lifecycleScope = CoroutineScope(Dispatchers.IO + job)
    @Inject lateinit var activityRepository: DataRepository

    private object Constants {
        const val REQUEST_CODE_INTENT_ACTIVITY_TRANSITION = 0
        const val TAG = "ACTIVITY_RECOGNITION"
    }

    private lateinit var activityRecognitionClient: ActivityRecognitionClient
    override fun onCreate() {
        super.onCreate()
        Log.d(Constants.TAG, "Activity client was created")
        activityRecognitionClient = ActivityRecognition.getClient(this)
        requestActivityUpdates()
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

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        startForeground()
        return START_STICKY
    }

    private fun requestActivityUpdates() {
        val intent = Intent(this, ActivityTransitionReceiver::class.java)
        val pendingIntent = PendingIntent.getBroadcast(
            this,
            Constants.REQUEST_CODE_INTENT_ACTIVITY_TRANSITION,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
        )

        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACTIVITY_RECOGNITION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            Log.d(Constants.TAG, "Permission for activity recognition was denied")
            return
        }

        Log.d(Constants.TAG, "perms are there, start activity recognition")
        activityRecognitionClient.requestActivityUpdates(
            1000,
//            ActivityTransitionRequest(this.getActivityTransitions()),
            pendingIntent
        ).addOnSuccessListener {
            Log.d(Constants.TAG, "Registered for activity recognition")
            // Successfully registered for updates
        }.addOnFailureListener { e ->
            // Handle any errors
            Log.d(Constants.TAG, "Failed to register for activity recognition"+e.printStackTrace())
        }
    }

    private fun getActivityTransitions(): List<ActivityTransition> {
        return listOf(
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.WALKING)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                .build(),
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.WALKING)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                .build(),
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.STILL)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                .build(),
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.STILL)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                .build(),
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.IN_VEHICLE)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_ENTER)
                .build(),
            ActivityTransition.Builder()
                .setActivityType(DetectedActivity.IN_VEHICLE)
                .setActivityTransition(ActivityTransition.ACTIVITY_TRANSITION_EXIT)
                .build()
        )
    }

    fun updateActivity(activity: HumanActivity) {
        lifecycleScope.launch {
            activityRepository.updateActivity(activity)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        Log.d(Constants.TAG, "destroyed activity service")
    }
}

class ActivityTransitionReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Log.d("ACTIVITY_RECOGNITION", "received intent")
        if (ActivityRecognitionResult.hasResult(intent)) {
            val result = ActivityRecognitionResult.extractResult(intent)
            result?.let {
                    val activityType = toActivityString(result.mostProbableActivity.type)
                    Log.d("ACTIVITY_RECOGNITION", "Transition: $activityType")
                    if (context is ActivityDetectionService) {
                        Log.d("ACTIVITY_RECOGNITION", "Correct context")
                        context.updateActivity(HumanActivity(activityType))
                }
            }
        }
        if (ActivityTransitionResult.hasResult(intent)) {
            val result = ActivityTransitionResult.extractResult(intent)
            result?.let {
                for (event in it.transitionEvents) {
                    val activityType = toActivityString(event.activityType)
                    val transitionType = toTransitionType(event.transitionType)
                    Log.d("ActivityRecognition", "Transition: $activityType $transitionType")
                    if (context is ActivityDetectionService) {
                        context.updateActivity(HumanActivity(activityType))
                    }
                }
            }
        }
    }

    private fun toActivityString(activity: Int): String {
        return when (activity) {
            DetectedActivity.STILL -> "STILL"
            DetectedActivity.WALKING -> "WALKING"
            DetectedActivity.RUNNING -> "RUNNING"
            DetectedActivity.IN_VEHICLE -> "IN VEHICLE"
            else -> "UNKNOWN"
        }
    }

    private fun toTransitionType(transitionType: Int): String {
        return when (transitionType) {
            ActivityTransition.ACTIVITY_TRANSITION_ENTER -> "ENTER"
            ActivityTransition.ACTIVITY_TRANSITION_EXIT -> "EXIT"
            else -> "UNKNOWN"
        }
    }
}