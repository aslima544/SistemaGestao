#!/bin/bash
echo "🚀 Iniciando frontend..."
echo "📁 Verificando build..."
ls -la build/ | head -5

echo "🌐 Configurações de rede:"
echo "PORT: ${PORT:-'não definido'}"
echo "HOST: 0.0.0.0 (padrão serve)"

echo "🎯 Iniciando servidor..."
npx serve -s build -p ${PORT:-3000}