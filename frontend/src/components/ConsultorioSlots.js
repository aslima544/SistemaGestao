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

  // Verifica se é final de semana (sábado = 6, domingo = 0)
  const dataVerificacao = new Date(ano, mes - 1, dia);
  const diaSemana = dataVerificacao.getDay();
  const isFinalSemana = diaSemana === 0 || diaSemana === 6; // domingo = 0, sábado = 6

  // Lista de feriados (formato YYYY-MM-DD) - pode ser expandida
  const feriados = [
    '2025-01-01', // Confraternização Universal
    '2025-04-21', // Tiradentes
    '2025-05-01', // Dia do Trabalhador
    '2025-09-07', // Independência do Brasil
    '2025-10-12', // Nossa Senhora Aparecida
    '2025-11-02', // Finados
    '2025-11-15', // Proclamação da República
    '2025-12-25', // Natal
    // Adicionar outros feriados locais conforme necessário
  ];
  
  const isFeriado = feriados.includes(dataAgendamento);
  const isDiaIndisponivel = isFinalSemana || isFeriado;

  // Mostrar aviso se for dia indisponível
  if (isDiaIndisponivel) {
    const motivoIndisponibilidade = isFeriado ? 'feriado' : 'final de semana';
    return (
      <div>
        <h3>Horários do {consultorio.name}</h3>
        <div style={{ 
          padding: '20px', 
          backgroundColor: '#fef3c7', 
          border: '1px solid #f59e0b',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <p style={{ margin: 0, color: '#92400e', fontWeight: 'bold' }}>
            ⚠️ Unidade fechada em {motivoIndisponibilidade}
          </p>
          <p style={{ margin: '8px 0 0 0', color: '#92400e', fontSize: '14px' }}>
            Selecione um dia útil (segunda a sexta-feira) para agendar consultas.
          </p>
        </div>
      </div>
    );
  }

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

          // Só procura agendamento se o slot NÃO for passado
          let agendamento = null;
          let ocupado = false;
          if (!slotPassado) {
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
              const end = start + (a.duration_minutes || 30);

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