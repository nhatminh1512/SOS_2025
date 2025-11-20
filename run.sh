#!/bin/bash
# Script để chạy ứng dụng Streamlit

# Port mặc định
PORT=${1:-8501}

echo "🚀 Đang khởi động ứng dụng trên port $PORT..."
echo "📍 Truy cập tại: http://localhost:$PORT"
echo ""

streamlit run app.py --server.port $PORT

