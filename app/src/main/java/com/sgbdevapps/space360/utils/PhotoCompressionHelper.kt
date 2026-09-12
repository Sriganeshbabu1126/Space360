package com.sgbdevapps.space360.utils

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Log
import java.io.ByteArrayOutputStream
import java.io.File

object PhotoCompressionHelper {
    
    private const val MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  // 5 MB
    private const val TARGET_WIDTH = 1920
    private const val TARGET_HEIGHT = 1080
    private const val COMPRESSION_QUALITY_HIGH = 90
    private const val COMPRESSION_QUALITY_LOW = 70
    
    data class CompressionResult(
        val success: Boolean,
        val compressedFilePath: String? = null,
        val originalSizeBytes: Long = 0,
        val compressedSizeBytes: Long = 0,
        val message: String = ""
    )
    
    fun compressPhotoIfNeeded(
        context: Context,
        sourceUri: Uri
    ): CompressionResult {
        return try {
            val originalFile = getFileFromUri(context, sourceUri)
            val originalSizeBytes = originalFile.length()
            
            Log.d("PhotoCompression", "Original photo size: ${originalSizeBytes / 1024} KB")
            
            if (originalSizeBytes <= MAX_FILE_SIZE_BYTES) {
                Log.d("PhotoCompression", "Photo size OK, no compression needed")
                return CompressionResult(
                    success = true,
                    compressedFilePath = originalFile.absolutePath,
                    originalSizeBytes = originalSizeBytes,
                    compressedSizeBytes = originalSizeBytes,
                    message = "Photo ready (${originalSizeBytes / 1024} KB)"
                )
            }
            
            Log.d("PhotoCompression", "Photo exceeds limit, compressing...")
            val compressedFile = compressPhoto(context, sourceUri)
            val compressedSizeBytes = compressedFile.length()
            
            if (compressedSizeBytes > MAX_FILE_SIZE_BYTES) {
                Log.w("PhotoCompression", "Compression failed: Still > 5MB (${compressedSizeBytes / 1024} KB)")
                return CompressionResult(
                    success = false,
                    originalSizeBytes = originalSizeBytes,
                    compressedSizeBytes = compressedSizeBytes,
                    message = "Photo too large even after compression (${compressedSizeBytes / 1024} KB). Please choose a smaller image."
                )
            }
            
            val compressionPercent = ((originalSizeBytes - compressedSizeBytes) * 100) / originalSizeBytes
            Log.d("PhotoCompression", "Compression successful: ${compressionPercent}% reduction")
            
            CompressionResult(
                success = true,
                compressedFilePath = compressedFile.absolutePath,
                originalSizeBytes = originalSizeBytes,
                compressedSizeBytes = compressedSizeBytes,
                message = "Photo compressed (${originalSizeBytes / 1024} KB → ${compressedSizeBytes / 1024} KB)"
            )
            
        } catch (e: Exception) {
            Log.e("PhotoCompression", "Error compressing photo", e)
            CompressionResult(
                success = false,
                message = "Error processing photo: ${e.message}"
            )
        }
    }
    
    private fun compressPhoto(context: Context, sourceUri: Uri): File {
        val originalBitmap = BitmapFactory.decodeStream(context.contentResolver.openInputStream(sourceUri))
            ?: throw Exception("Could not decode image")
        
        val scaledBitmap = scaleBitmap(originalBitmap, TARGET_WIDTH, TARGET_HEIGHT)
        var compressedBytes = compressBitmap(scaledBitmap, COMPRESSION_QUALITY_HIGH)
        
        if (compressedBytes.size > MAX_FILE_SIZE_BYTES) {
            Log.d("PhotoCompression", "High quality too large, trying lower quality...")
            compressedBytes = compressBitmap(scaledBitmap, COMPRESSION_QUALITY_LOW)
        }
        
        val outputFile = File(context.cacheDir, "compressed_photo_${System.currentTimeMillis()}.jpg")
        outputFile.writeBytes(compressedBytes)
        
        originalBitmap.recycle()
        scaledBitmap.recycle()
        
        return outputFile
    }
    
    private fun scaleBitmap(original: Bitmap, maxWidth: Int, maxHeight: Int): Bitmap {
        val ratio = original.width.toFloat() / original.height.toFloat()
        val newWidth: Int
        val newHeight: Int
        
        if (original.width > original.height) {
            newWidth = minOf(original.width, maxWidth)
            newHeight = (newWidth / ratio).toInt()
        } else {
            newHeight = minOf(original.height, maxHeight)
            newWidth = (newHeight * ratio).toInt()
        }
        
        return Bitmap.createScaledBitmap(original, newWidth, newHeight, true)
    }
    
    private fun compressBitmap(bitmap: Bitmap, quality: Int): ByteArray {
        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, quality, stream)
        return stream.toByteArray()
    }
    
    private fun getFileFromUri(context: Context, uri: Uri): File {
        val inputStream = context.contentResolver.openInputStream(uri)
            ?: throw Exception("Could not open URI: $uri")
        
        val file = File(context.cacheDir, "temp_photo_${System.currentTimeMillis()}.jpg")
        file.outputStream().use { outputStream ->
            inputStream.copyTo(outputStream)
        }
        
        return file
    }
}
