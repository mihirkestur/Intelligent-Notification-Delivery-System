package com.example.activitycollector

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.example.activitycollector.ui.theme.ActivityCollectorTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (!hasNotificationAccess(applicationContext)) {
            openPermissions()
        }
        val intent = Intent(this, Notifications::class.java)
        startForegroundService(intent)
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
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    ActivityCollectorTheme {
        Greeting("Android")
    }
}