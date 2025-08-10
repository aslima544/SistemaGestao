# Configuração fixa para Railway
# Este arquivo força as configurações corretas

import os

def get_mongo_url():
    """Força Atlas em produção, localhost em dev"""
    
    # Se tem PORT ou RAILWAY_ENVIRONMENT = é Railway
    if os.getenv("PORT") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
        return "mongodb+srv://admin:senha45195487@cluster0.8skwoca.mongodb.net/sistema_consultorio?retryWrites=true&w=majority&appName=Cluster0"
    
    # Desenvolvimento local
    return os.getenv("MONGO_URL", "mongodb://localhost:27017")

def get_database_name():
    """Nome do banco correto"""
    return "sistema_consultorio"