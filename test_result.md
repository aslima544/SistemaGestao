# Sistema de Gestão de Consultórios - Testing Protocol

## Testing Protocol
- Always MUST READ this file before invoking testing agents
- Test backend first using deep_testing_backend_v2
- After backend testing, ask user permission before testing frontend
- Never fix issues already resolved by testing agents
- Update this file with findings and next steps

## Current Investigation: C3 14:30 Slot Not Updating Visually

### Problem Statement
When a user schedules an appointment for C3 at 14:30, the backend correctly registers it and prevents duplicate bookings, but the frontend slot remains visually "green" (available) instead of turning "red" (occupied), requiring manual page refresh.

### Investigation Status
INVESTIGATING - Examining frontend state management and data synchronization

### Testing History
- No previous testing recorded

### Next Steps
1. Test backend appointment creation for C3 14:30
2. Verify frontend state updates after appointment creation
3. Debug ConsultorioSlots.js rendering logic

## Incorporate User Feedback
User is experiencing: "slot C3 14:30 não atualiza para vermelho após criação do agendamento, mesmo com o agendamento existindo no backend"

Focus on real-time visual updates without page refresh.