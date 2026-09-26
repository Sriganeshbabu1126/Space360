# Setup Script for GCP Monitoring Alert Policies
# Requires `gcloud alpha` components to be installed.
# To install components: gcloud components install alpha

$PROJECT_ID = "space360-114433"

Write-Host "Creating CPU Alert Policy..."
gcloud alpha monitoring policies create --policy-from-file=cpu_alert.json --project=$PROJECT_ID

Write-Host "Creating Memory Alert Policy..."
gcloud alpha monitoring policies create --policy-from-file=memory_alert.json --project=$PROJECT_ID

Write-Host "Creating Error Rate Alert Policy..."
gcloud alpha monitoring policies create --policy-from-file=error_rate_alert.json --project=$PROJECT_ID

Write-Host "Alert policies setup complete!"
