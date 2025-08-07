import React from 'react';
import { gerarSlots } from '../utils/slots';

function ConsultorioSlots({ consultorio, agendamentos, dataSelecionada, onAgendar, onCancelarAgendamento }) {
  if (!consultorio) return null;

  // Pega o horário de início e fim do consultório
  const inicio = consultorio.fixed_schedule
    ? consultorio.fixed_schedule.start
    : "07:00";
  const fim = consultorio.fixed_schedule
    ? consultorio.fixed_schedule.end
    : "19:00";
  const slots = gerarSlots(inicio, fim);

  // Usa a data selecionada (formato "YYYY-MM-DD") ou hoje como fallback
  const dataAgendamento = dataSelecionada || new Date().toISOString().slice(0, 10);
  const [ano, mes, dia] = dataAgendamento.split('-').map(Number);
  
  // Remove debug logs - system ready for production
  // const agendamentosC3 = agendamentos?.filter(a => a.consultorio_id === consultorio.id) || [];
  // const agendamentosHoje = agendamentosC3.filter(a => {
  //   if (!a.appointment_date) return false;
  //   const aptDate = new Date(a.appointment_date);
  //   const aptDateStr = aptDate.toISOString().slice(0, 10);
  //   return aptDateStr === dataAgendamento;
  // });

  return (
    <div>
      <h3>Horários do {consultorio.name}</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {slots.map(horario => {
          // Verifica se o slot já passou
          const [sh, sm] = horario.split(':').map(Number);
          const dataSlot = new Date(ano, mes - 1, dia, sh, sm, 0, 0);
          const agora = new Date();
          const slotPassado = dataSlot < agora;

          // Procura agendamento para QUALQUER horário (passado ou futuro)
          let agendamento = null;
          let ocupado = false;
          
          // CORREÇÃO: Sempre verifica ocupação, independente se o slot já passou
          agendamento = agendamentos.find(a => {
            if (!a.appointment_date) return false;
            if (a.consultorio_id !== consultorio.id) return false;
            
            // Extract date and time from appointment_date
            const appointmentDate = new Date(a.appointment_date);
            const appointmentDateStr = appointmentDate.toISOString().slice(0, 10);
            
            // Check if it's the same date
            if (appointmentDateStr !== dataAgendamento) return false;
            
            // Extract hour and minute from appointment_date
            const appointmentHour = appointmentDate.getHours();
            const appointmentMinute = appointmentDate.getMinutes();
            const start = appointmentHour * 60 + appointmentMinute;
            const end = start + (a.duration || 30);

            const slotTime = sh * 60 + sm;

            return slotTime >= start && slotTime < end && a.status !== "canceled";
          });
          ocupado = !!agendamento;
          }

          return (
            <div key={horario} style={{ position: 'relative', display: 'inline-block' }}>
              <button
                disabled={ocupado || slotPassado}
                style={{
                  background: ocupado
                    ? '#ef4444'
                    : slotPassado
                    ? '#e5e7eb'
                    : '#a7f3d0',
                  color: ocupado
                    ? '#fff'
                    : slotPassado
                    ? '#888'
                    : '#000',
                  cursor: ocupado || slotPassado ? 'not-allowed' : 'pointer',
                  padding: '8px',
                  border: '1px solid #888',
                  borderRadius: '4px',
                  margin: '2px',
                  fontWeight: ocupado ? 'bold' : 'normal',
                  minWidth: 90,
                  minHeight: 50,
                  height: 50,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center',
                  position: 'relative'
                }}
                onClick={() => !ocupado && !slotPassado && onAgendar(horario)}
                title={
                  ocupado && agendamento
                    ? "Ocupado"
                    : slotPassado
                    ? "Horário indisponível"
                    : "Clique para agendar"
                }
              >
                {horario}
                {ocupado && agendamento && (
                  <div style={{ fontSize: '0.7em', marginTop: 2 }}>
                    Ocupado
                  </div>
                )}
                {!ocupado && slotPassado && (
                  <div style={{ fontSize: '0.7em', marginTop: 2 }}>
                    Indisponível
                  </div>
                )}
              </button>
              {ocupado && agendamento && (
                <button
                  style={{
                    position: 'absolute',
                    top: 2,
                    right: 2,
                    fontSize: '0.8em',
                    background: '#fff',
                    color: '#ef4444',
                    border: 'none',
                    cursor: 'pointer',
                    zIndex: 2
                  }}
                  onClick={e => {
                    e.stopPropagation();
                    onCancelarAgendamento(agendamento);
                  }}
                  title="Liberar horário"
                >
                  ❌
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ConsultorioSlots;