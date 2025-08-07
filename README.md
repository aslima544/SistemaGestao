# Sistema de Gestão de Consultórios

Sistema completo para gerenciamento de consultórios médicos com agendamentos.

## Deploy no Railway

### Configuração de Banco MongoDB
1. Crie um banco MongoDB gratuito no MongoDB Atlas
2. Configure as variáveis de ambiente no Railway:
   - `MONGO_URL`: sua string de conexão do MongoDB Atlas
   - `JWT_SECRET`: uma chave secreta aleatória (ex: sua-chave-secreta-123)

### Funcionalidades
- ✅ Dashboard com estatísticas
- ✅ Gestão de Pacientes, Médicos, Consultórios
- ✅ Sistema de Agendamentos com sincronização visual
- ✅ Horários flexíveis por consultório
- ✅ Controle de acesso por papel (Admin, Médico, Recepção)
- ✅ Timezone configurado para GMT-3 (Brasil)

### Usuários Padrão
- **Admin**: admin / admin123
- **Médico**: medico / medico123
- **Recepção**: recepcao / recepcao123

### Tecnologias
- Backend: FastAPI (Python)
- Frontend: React + Tailwind CSS
- Banco: MongoDB
- Deploy: Railway

### Suporte
Sistema desenvolvido na plataforma Emergent AI.
