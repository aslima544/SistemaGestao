import React from 'react';
import horariosConsultorios from '../constants/horariosConsultorios';

function ConsultorioSlots({ consultorio, agendamentos, dataSelecionada, onAgendar, onCancelarAgendamento }) {
  if (!consultorio) return null;

  // Configuração simples e clara
  const dataHoje = dataSelecionada || new Date().toISOString().slice(0, 10);
  const horarioInfo = horariosConsultorios[consultorio.name] || { inicio: "08:00", fim: "17:00" };
  
  // Criar lista de slots de 15 em 15 minutos
  const gerarSlots = () => {
    const slots = [];
    const [inicioHora, inicioMin] = horarioInfo.inicio.split(':').map(Number);
    const [fimHora, fimMin] = horarioInfo.fim.split(':').map(Number);
    
    const inicioMinutos = inicioHora * 60 + inicioMin;
    const fimMinutos = fimHora * 60 + fimMin;
    
    for (let minutos = inicioMinutos; minutos < fimMinutos; minutos += 15) {
      const horas = Math.floor(minutos / 60);
      const mins = minutos % 60;
      const horario = `${horas.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
      slots.push(horario);
    }
    
    return slots;
  };

  // Criar mapa de agendamentos para busca rápida
  const mapaAgendamentos = {};
  console.log('🔍 NOVA DEBUG:', {
    consultorio_name: consultorio.name,
    consultorio_id: consultorio.id,
    dataHoje,
    total_agendamentos: agendamentos.length
  });
  
  agendamentos.forEach(agendamento => {
    // Debug cada agendamento
    if (agendamento.consultorio_id === consultorio.id) {
      console.log('🎯 AGENDAMENTO C3:', {
        id: agendamento.id,
        appointment_date: agendamento.appointment_date,
        status: agendamento.status,
        duration: agendamento.duration
      });
    }
    
    // Só processar agendamentos do consultório atual e da data atual
    if (agendamento.consultorio_id !== consultorio.id) return;
    
    const dataAgendamento = new Date(agendamento.appointment_date);
    const dataStr = dataAgendamento.toISOString().slice(0, 10);
    
    console.log('📅 COMPARAÇÃO DATA:', {
      dataStr,
      dataHoje,
      match: dataStr === dataHoje
    });
    
    if (dataStr !== dataHoje) return;
    
    // Calcular todos os slots que este agendamento ocupa
    const horaInicio = dataAgendamento.getHours();
    const minInicio = dataAgendamento.getMinutes();
    const duracao = agendamento.duration || 30;
    
    console.log('⏰ SLOTS OCUPADOS:', {
      horaInicio,
      minInicio,
      duracao,
      status: agendamento.status
    });
    
    const inicioMinutos = horaInicio * 60 + minInicio;
    const fimMinutos = inicioMinutos + duracao;
    
    // Marcar todos os slots ocupados por este agendamento
    for (let minutos = inicioMinutos; minutos < fimMinutos; minutos += 15) {
      const horas = Math.floor(minutos / 60);
      const mins = minutos % 60;
      const slot = `${horas.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
      
      mapaAgendamentos[slot] = {
        agendamento: agendamento,
        ocupado: agendamento.status !== 'canceled'
      };
      
      console.log('🔴 SLOT MARCADO:', slot, 'ocupado:', agendamento.status !== 'canceled');
    }
  });
  
  console.log('📊 MAPA FINAL:', mapaAgendamentos);

  const slots = gerarSlots();

  return (
    <div style={{ padding: '20px' }}>
      <h3 style={{ marginBottom: '20px', color: '#333' }}>
        {consultorio.name} - Horários para {dataHoje.split('-').reverse().join('/')}
      </h3>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))', 
        gap: '8px',
        maxWidth: '600px'
      }}>
        {slots.map(horario => {
          const slotInfo = mapaAgendamentos[horario];
          const agora = new Date();
          const [h, m] = horario.split(':').map(Number);
          const slotData = new Date(dataHoje + 'T' + horario + ':00');
          const jaPassou = slotData < agora;
          
          // Estados possíveis: ocupado, passou, disponível
          let cor = '#a7f3d0'; // verde (disponível)
          let texto = horario;
          let desabilitado = false;
          let onClick = () => onAgendar(horario);
          
          if (slotInfo && slotInfo.ocupado) {
            // OCUPADO - VERMELHO
            cor = '#ef4444';
            texto = horario;
            desabilitado = true;
            onClick = null;
          } else if (jaPassou) {
            // JÁ PASSOU - CINZA
            cor = '#9ca3af';
            texto = horario;
            desabilitado = true;
            onClick = null;
          }
          
          return (
            <button
              key={horario}
              disabled={desabilitado}
              style={{
                backgroundColor: cor,
                color: jaPassou ? '#6b7280' : (slotInfo && slotInfo.ocupado ? 'white' : '#1f2937'),
                border: 'none',
                borderRadius: '6px',
                padding: '8px 4px',
                fontSize: '12px',
                fontWeight: '500',
                cursor: desabilitado ? 'not-allowed' : 'pointer',
                opacity: desabilitado ? 0.7 : 1,
                transition: 'all 0.2s',
                position: 'relative'
              }}
              onClick={onClick}
              onMouseOver={(e) => {
                if (!desabilitado) {
                  e.target.style.transform = 'scale(1.05)';
                }
              }}
              onMouseOut={(e) => {
                e.target.style.transform = 'scale(1)';
              }}
            >
              {texto}
              
              {/* Botão de cancelar para slots ocupados */}
              {slotInfo && slotInfo.ocupado && (
                <button
                  style={{
                    position: 'absolute',
                    top: '-4px',
                    right: '-4px',
                    background: '#dc2626',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '16px',
                    height: '16px',
                    fontSize: '10px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onCancelarAgendamento(slotInfo.agendamento);
                  }}
                >
                  ×
                </button>
              )}
            </button>
          );
        })}
      </div>
      
      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: '#a7f3d0', borderRadius: '3px' }}></div>
            <span>Disponível</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: '#ef4444', borderRadius: '3px' }}></div>
            <span>Ocupado</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div style={{ width: '16px', height: '16px', backgroundColor: '#9ca3af', borderRadius: '3px' }}></div>
            <span>Passou</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConsultorioSlots;