package com.example.activitycollector

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

data class HumanActivity constructor(val activity: String)

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "activity_datastore")

@Module
@InstallIn(SingletonComponent::class)
object DataStoreModule {
    @Provides
    @Singleton
    fun providePreferencesDataStore(@ApplicationContext appContext: Context): DataStore<Preferences> {
        return appContext.dataStore
    }
}

class DataRepository @Inject constructor(private val dataStore: DataStore<Preferences>) {
    private val activityKey = stringPreferencesKey("activity")

    companion object {
        const val NOT_DETECTED = "NOT_DETECTED"
    }

    private val mapToHumanActivity: Flow<HumanActivity> = dataStore.data.map { preferences ->
        HumanActivity(preferences[activityKey] ?: NOT_DETECTED)
    }

    suspend fun updateActivity(activity: HumanActivity) {
        dataStore.edit { preferences -> preferences[activityKey] = activity.activity }
    }

    suspend fun readActivity(): HumanActivity {
        return mapToHumanActivity.first()
    }
}