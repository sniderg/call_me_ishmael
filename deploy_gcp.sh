#!/bin/bash

# Ensure .env variables are available
# We use python to robustly read the .env file (handling spaces/quotes correctly)
if [ -f .env ]; then
  eval $(uv run python3 -c "from dotenv import dotenv_values; print('\n'.join([f'export {k}=\"{v}\"' for k, v in dotenv_values('.env').items()]))")
fi

# Verify required variables are set
REQUIRED_VARS=("PROJECT_ID" "REGION" "FUNCTION_NAME" "BUCKET_NAME" "GMAIL_USER" "GMAIL_APP_PASSWORD" "TARGET_EMAIL")
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR}" ]; then
    echo "Error: $VAR is not set. Please check your .env file."
    exit 1
  fi
done

# Strip spaces from App Password if present (just in case they were preserved)
GMAIL_APP_PASSWORD="${GMAIL_APP_PASSWORD// /}"

echo "Deploying Cloud Function..."

gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python311 \
    --region=$REGION \
    --source=. \
    --entry-point=daily_emailer \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars GCS_BUCKET_NAME=$BUCKET_NAME,GMAIL_USER=$GMAIL_USER,GMAIL_APP_PASSWORD=$GMAIL_APP_PASSWORD,TARGET_EMAIL=$TARGET_EMAIL

echo "Function URL:"
FUNC_URL=$(gcloud functions describe $FUNCTION_NAME --gen2 --region=$REGION --format='value(serviceConfig.uri)')
echo $FUNC_URL

echo "Creating Cloud Scheduler Job (Daily at 7 AM)..."
gcloud scheduler jobs create http ${FUNCTION_NAME}-trigger \
    --location=$REGION \
    --schedule="0 7 * * *" \
    --uri=$FUNC_URL \
    --http-method=GET \
    --time-zone="America/New_York"

echo "Deployment complete!"
