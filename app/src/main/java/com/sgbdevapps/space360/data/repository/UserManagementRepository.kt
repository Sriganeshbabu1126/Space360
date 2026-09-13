package com.sgbdevapps.space360.data.repository

import android.content.Context
import com.google.api.client.googleapis.auth.oauth2.GoogleCredential
import com.google.auth.http.HttpCredentialsAdapter
import com.google.auth.oauth2.GoogleCredentials
import com.google.api.client.http.javanet.NetHttpTransport
import com.google.api.client.json.gson.GsonFactory
import com.google.api.services.sheets.v4.Sheets
import com.google.api.services.sheets.v4.SheetsScopes
import com.google.api.services.sheets.v4.model.ValueRange
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseAuthUserCollisionException
import com.google.firebase.auth.userProfileChangeRequest
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.tasks.await
import kotlinx.coroutines.withContext
import timber.log.Timber
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject

class UserManagementRepository @Inject constructor(
    @ApplicationContext private val context: Context,
    private val apiService: com.sgbdevapps.space360.data.remote.AuthService
) {
    companion object {
        const val SHEET_ID = "YOUR_SPACE360_CRED_SHEET_ID_HERE"
        const val SHEET_NAME = "SPACE360-CRED"
        const val DUMMY_PASSWORD = "welcomespace360"
    }

    suspend fun createNewUser(
        name: String,
        email: String,
        role: String
    ): Result<String> = withContext(Dispatchers.IO) {
        try {
            val authResult = FirebaseAuth.getInstance()
                .createUserWithEmailAndPassword(email, DUMMY_PASSWORD)
                .await()

            val uid = authResult.user?.uid
                ?: return@withContext Result.failure(Exception("Firebase user creation failed"))

            val profileUpdate = userProfileChangeRequest {
                displayName = name
            }
            authResult.user?.updateProfile(profileUpdate)?.await()

            writeUserToSheet(
                uid = uid,
                name = name,
                email = email,
                role = role,
                password = DUMMY_PASSWORD,
                status = "MUST_CHANGE_PASSWORD"
            )
            
            try {
                apiService.notifyNewUser(com.sgbdevapps.space360.data.remote.NotifyUserRequest(
                    name = name,
                    email = email,
                    temp_password = DUMMY_PASSWORD
                ))
                Timber.i("Welcome email sent to $email")
            } catch (e: Exception) {
                Timber.w("Welcome email failed — user still created: ${e.message}")
            }

            Timber.i("New user created: $email (uid=$uid)")
            Result.success(uid)

        } catch (e: FirebaseAuthUserCollisionException) {
            Result.failure(Exception("A user with this email already exists"))
        } catch (e: Exception) {
            Timber.e(e, "Failed to create user: $email")
            Result.failure(e)
        }
    }

    private fun writeUserToSheet(
        uid: String,
        name: String,
        email: String,
        role: String,
        password: String,
        status: String
    ) {
        try {
            // TODO: Provide service_account.json manually.
            // 1. Go to Google Cloud Console -> IAM & Admin -> Service Accounts
            // 2. Create service account: "space360-sheets-writer"
            // 3. Grant role: "Google Sheets Editor"
            // 4. Create JSON key -> download -> rename to service_account.json
            // 5. Place service_account.json in app/src/main/assets/
            val credentials = GoogleCredentials.fromStream(
                context.assets.open("service_account.json")
            ).createScoped(listOf(SheetsScopes.SPREADSHEETS))

            val transport = NetHttpTransport()
            val jsonFactory = GsonFactory.getDefaultInstance()

            val service = Sheets.Builder(transport, jsonFactory, HttpCredentialsAdapter(credentials))
                .setApplicationName("Space360")
                .build()

            val now = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date())

            val row = listOf(listOf(uid, name, email, role, password, status, now))
            val body = ValueRange().setValues(row)

            service.spreadsheets().values()
                .append(SHEET_ID, "$SHEET_NAME!A:G", body)
                .setValueInputOption("RAW")
                .execute()

            Timber.i("User written to SPACE360-CRED sheet: $email")
        } catch (e: Exception) {
            Timber.e(e, "Failed to write to Google Sheets - user still created in Firebase")
        }
    }

    suspend fun markPasswordChanged(email: String, newPassword: String) {
        withContext(Dispatchers.IO) {
            try {
                val credentials = GoogleCredentials.fromStream(
                    context.assets.open("service_account.json")
                ).createScoped(listOf(SheetsScopes.SPREADSHEETS))

                val transport = NetHttpTransport()
                val jsonFactory = GsonFactory.getDefaultInstance()

                val service = Sheets.Builder(transport, jsonFactory, HttpCredentialsAdapter(credentials))
                    .setApplicationName("Space360")
                    .build()

                val response = service.spreadsheets().values()
                    .get(SHEET_ID, "$SHEET_NAME!A:G")
                    .execute()

                val values = response.getValues() ?: return@withContext
                val rowIndex = values.indexOfFirst { row ->
                    row.getOrNull(2)?.toString() == email
                }

                if (rowIndex >= 0) {
                    val sheetRow = rowIndex + 1  // Sheets API is 1-indexed
                    val now = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault()).format(Date())
                    val updateBody = ValueRange().setValues(
                        listOf(listOf("", "", "", "", newPassword, "ACTIVE", now))
                    )
                    service.spreadsheets().values()
                        .update(SHEET_ID, "$SHEET_NAME!A${sheetRow}:G${sheetRow}", updateBody)
                        .setValueInputOption("RAW")
                        .execute()

                    Timber.i("Password updated in sheet for: $email")
                }
            } catch (e: Exception) {
                Timber.e(e, "Failed to update sheet password - Firebase already updated")
            }
        }
    }
}
