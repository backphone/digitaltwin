#!/bin/bash

echo "🔄 [$(date)] Starting retraining pipeline..." >> /home/ubuntu/ai_env/logs/auto_retrain.log

# Step 1: Retrain from feedback
python3 /home/ubuntu/ai_env/retrain_from_feedback.py >> /home/ubuntu/ai_env/logs/auto_retrain.log 2>&1

# Step 2: Merge new feedback into the main FAISS index
python3 /home/ubuntu/ai_env/merge_faiss.py >> /home/ubuntu/ai_env/logs/auto_retrain.log 2>&1

# Step 3: Restart Flask app
pkill -f app.py
nohup python3 /home/ubuntu/ai_env/app.py >> /home/ubuntu/ai_env/logs/app_restart.log 2>&1 &

echo "✅ [$(date)] Retraining and restart complete." >> /home/ubuntu/ai_env/logs/auto_retrain.log
