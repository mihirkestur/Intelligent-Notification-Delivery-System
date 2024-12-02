package com.example.activitycollector

import android.Manifest
import android.app.ActivityManager
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.tooling.preview.Preview
import androidx.core.app.ActivityCompat
import androidx.core.content.PermissionChecker
import com.example.activitycollector.ui.theme.ActivityCollectorTheme
import dagger.hilt.android.AndroidEntryPoint


@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!hasNotificationAccess(applicationContext)) {
            openPermissions()
        }
        val notificationServiceIntent = Intent(this, Notifications::class.java)
        val activityRecognitionIntent = Intent(this, ActivityDetectionService::class.java)

        startForegroundService(notificationServiceIntent)
        startForegroundService(activityRecognitionIntent)
        enableEdgeToEdge()
        setContent {
            ActivityCollectorTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    Greeting(
                        name = "Android",
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }

    }

    private fun isMyServiceRunning(serviceClass: Class<*>): Boolean {
        val manager = getSystemService(ACTIVITY_SERVICE) as ActivityManager
        for (service in manager.getRunningServices(Int.MAX_VALUE)) {
            if (serviceClass.name == service.service.className) {
                return true
            }
        }
        return false
    }

    fun onClickListener() {
        val activity = arrayOf(Manifest.permission.ACTIVITY_RECOGNITION)
        val foreground = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
        val background = arrayOf(Manifest.permission.ACCESS_BACKGROUND_LOCATION)


        val perm1 = ActivityCompat.checkSelfPermission(
            this,
            Manifest.permission.ACTIVITY_RECOGNITION
        ) == PermissionChecker.PERMISSION_DENIED
        val perm2 = ActivityCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PermissionChecker.PERMISSION_DENIED
        val perm3 = ActivityCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PermissionChecker.PERMISSION_DENIED
        val perm4 = ActivityCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_BACKGROUND_LOCATION
        ) == PermissionChecker.PERMISSION_DENIED


        if (perm2 || perm3) {
            Log.e("tag", "2")
            ActivityCompat.requestPermissions(this, foreground, 200)
        } else if (perm4) {
            Log.e("tag", "3")
            ActivityCompat.requestPermissions(this, background, 300)
        } else if (perm1) {
            Log.e("tag", "1")
            ActivityCompat.requestPermissions(this, activity, 100)
        } else {
            Log.e("TAG", "permission ok")
        }

        val isActivityServiceRunning = isMyServiceRunning(ActivityDetectionService::class.java)
        Log.d("MAIN_ACTIVITY", "service is running?:$isActivityServiceRunning")
    }
    private fun hasNotificationAccess(context: Context): Boolean {
        return Settings.Secure.getString(
            context.applicationContext.contentResolver,
            "enabled_notification_listeners"
        ).contains(context.applicationContext.packageName)
    }

    private fun openPermissions() {
        try {
            val settingsIntent =
                Intent("android.settings.ACTION_NOTIFICATION_LISTENER_SETTINGS")
            startActivity(settingsIntent)
        } catch (e: ActivityNotFoundException) {
            e.printStackTrace()
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .fillMaxHeight(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(onClick = {
            if (context is MainActivity) {
                context.onClickListener()
            }
        }) {
            Text(text = "Show List")
        }
    }
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    ActivityCollectorTheme {
        Greeting("Android")
    }
}