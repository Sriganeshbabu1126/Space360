package com.sgbdevapps.space360.presentation.components

import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import android.util.Log

@Composable
fun QRCameraPreview(
    onQRDetected: (qrText: String) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember {
        ProcessCameraProvider.getInstance(context)
    }
    
    var detectedQRCode by remember { mutableStateOf("") }
    
    Box(modifier = Modifier.fillMaxSize()) {
        // Camera preview
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    this.scaleType = PreviewView.ScaleType.FILL_CENTER
                    cameraProviderFuture.addListener({
                        val cameraProvider = cameraProviderFuture.get()
                        
                        // Preview
                        val preview = Preview.Builder().build().also {
                            it.setSurfaceProvider(surfaceProvider)
                        }
                        
                        // Image analysis for barcode detection
                        val imageAnalysis = ImageAnalysis.Builder()
                            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                            .build()
                            .also { analysis ->
                                analysis.setAnalyzer(
                                    ContextCompat.getMainExecutor(ctx),
                                    QRCodeAnalyzer { qrText ->
                                        if (detectedQRCode != qrText) {
                                            detectedQRCode = qrText
                                            onQRDetected(qrText)
                                        }
                                    }
                                )
                            }
                        
                        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                        
                        try {
                            cameraProvider.unbindAll()
                            cameraProvider.bindToLifecycle(
                                lifecycleOwner,
                                cameraSelector,
                                preview,
                                imageAnalysis
                            )
                        } catch (exc: Exception) {
                            Log.e("QRCameraPreview", "Use case binding failed", exc)
                        }
                    }, ContextCompat.getMainExecutor(context))
                }
            },
            modifier = Modifier.fillMaxSize()
        )
        
        // Overlay: scanning frame
        Canvas(modifier = Modifier.fillMaxSize()) {
            val frameWidth = size.width * 0.75f
            val frameHeight = frameWidth * 0.9f
            val offsetX = (size.width - frameWidth) / 2
            val offsetY = (size.height - frameHeight) / 2
            
            // Semi-transparent background
            drawRect(
                color = Color.Black.copy(alpha = 0.5f),
                size = size
            )
            
            // Clear scanning frame
            drawRect(
                color = Color.Transparent,
                topLeft = Offset(offsetX, offsetY),
                size = Size(frameWidth, frameHeight),
                blendMode = BlendMode.Clear
            )
            
            // Frame border
            drawRect(
                color = Color.Green,
                topLeft = Offset(offsetX, offsetY),
                size = Size(frameWidth, frameHeight),
                style = Stroke(width = 4f)
            )
            
            // Corners
            val cornerSize = 30f
            drawLine(
                color = Color.Green,
                start = Offset(offsetX, offsetY),
                end = Offset(offsetX + cornerSize, offsetY),
                strokeWidth = 4f
            )
            drawLine(
                color = Color.Green,
                start = Offset(offsetX, offsetY),
                end = Offset(offsetX, offsetY + cornerSize),
                strokeWidth = 4f
            )
            // Other corners
            drawLine(
                color = Color.Green,
                start = Offset(offsetX + frameWidth, offsetY),
                end = Offset(offsetX + frameWidth - cornerSize, offsetY),
                strokeWidth = 4f
            )
            drawLine(
                color = Color.Green,
                start = Offset(offsetX + frameWidth, offsetY),
                end = Offset(offsetX + frameWidth, offsetY + cornerSize),
                strokeWidth = 4f
            )
            
            drawLine(
                color = Color.Green,
                start = Offset(offsetX, offsetY + frameHeight),
                end = Offset(offsetX + cornerSize, offsetY + frameHeight),
                strokeWidth = 4f
            )
            drawLine(
                color = Color.Green,
                start = Offset(offsetX, offsetY + frameHeight),
                end = Offset(offsetX, offsetY + frameHeight - cornerSize),
                strokeWidth = 4f
            )
            
            drawLine(
                color = Color.Green,
                start = Offset(offsetX + frameWidth, offsetY + frameHeight),
                end = Offset(offsetX + frameWidth - cornerSize, offsetY + frameHeight),
                strokeWidth = 4f
            )
            drawLine(
                color = Color.Green,
                start = Offset(offsetX + frameWidth, offsetY + frameHeight),
                end = Offset(offsetX + frameWidth, offsetY + frameHeight - cornerSize),
                strokeWidth = 4f
            )
        }
        
        // Instructions text
        Text(
            "Point camera at QR code",
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp),
            style = MaterialTheme.typography.bodyLarge,
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }
}

class QRCodeAnalyzer(
    private val onQRDetected: (String) -> Unit
) : ImageAnalysis.Analyzer {
    
    @androidx.annotation.OptIn(androidx.camera.core.ExperimentalGetImage::class)
    override fun analyze(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image ?: run {
            imageProxy.close()
            return
        }
        
        val image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )
        
        val scanner = BarcodeScanning.getClient()
        scanner.process(image)
            .addOnSuccessListener { barcodes ->
                for (barcode in barcodes) {
                    barcode.rawValue?.let { qrText ->
                        if (qrText.startsWith("space360://")) {
                            onQRDetected(qrText)
                        }
                    }
                }
            }
            .addOnFailureListener { e ->
                Log.e("QRCodeAnalyzer", "QR code scanning failed", e)
            }
            .addOnCompleteListener {
                imageProxy.close()
            }
    }
}
