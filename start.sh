#!/bin/bash
echo "🚀 Iniciando aplicação no Railway..."
echo "📁 Diretório atual: $(pwd)"
echo "📂 Arquivos disponíveis:"
ls -la

echo "🔍 Verificando Python e uvicorn..."
python --version
python -c "import uvicorn; print(f'Uvicorn version: {uvicorn.__version__}')"

echo "🔍 Verificando variáveis de ambiente..."
env | grep -i mongo || echo "Nenhuma variável MONGO encontrada"

echo "🌐 Iniciando servidor FastAPI..."
cd /app/backend || cd backend || cd /app
python -m uvicorn server_minimal:app --host 0.0.0.0 --port ${PORT:-8000}