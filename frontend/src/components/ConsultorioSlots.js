import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ConsultorioSlots = React.forwardRef(({ consultorio, dataSelecionada, onAgendar, onCancelarAgendamento }, ref) => {
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const dataHoje = dataSelecionada || new Date().toISOString().slice(0, 10);

  // Carrega slots do backend
  useEffect(() => {
    if (!consultorio) return;
    
    const carregarSlots = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await axios.get(
          `/api/consultorios/${consultorio.id}/slots?date=${dataHoje}`
        );
        
        setSlots(response.data.slots);
      } catch (err) {
        console.error('Erro ao carregar slots:', err);
        setError('Erro ao carregar horários disponíveis');
      } finally {
        setLoading(false);
      }
    };
    
    carregarSlots();
  }, [consultorio, dataHoje]);

  // Recarrega slots após ações (criar/cancelar agendamento)
  const recarregarSlots = async () => {
    if (!consultorio) return;
    
    try {
      const response = await axios.get(
        `/api/consultorios/${consultorio.id}/slots?date=${dataHoje}`
      );
      setSlots(response.data.slots);
    } catch (err) {
      console.error('Erro ao recarregar slots:', err);
    }
  };

  // Expor função de recarregar para o componente pai
  React.useImperativeHandle(ref, () => ({
    recarregar: recarregarSlots
  }), [consultorio, dataHoje]);

  if (!consultorio) return null;

  if (loading) {
    return (
      <div style={{ padding: '20px' }}>
        <h3 style={{ marginBottom: '20px', color: '#333' }}>
          {consultorio.name} - Carregando...
        </h3>
        <div>⏳ Carregando horários...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h3 style={{ marginBottom: '20px', color: '#333' }}>
          {consultorio.name} - Erro
        </h3>
        <div style={{ color: 'red' }}>{error}</div>
      </div>
    );
  }

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
        {slots.map(slot => {
          const { time, is_occupied, is_past, is_available, occupancy_info } = slot;
          
          // Determinar cor e estado
          let cor = '#a7f3d0'; // verde (disponível)
          let desabilitado = false;
          let onClick = () => {
            onAgendar(time);
          };
          
          if (is_occupied) {
            // OCUPADO - VERMELHO
            cor = '#ef4444';
            desabilitado = true;
            onClick = null;
          } else if (is_past) {
            // JÁ PASSOU - CINZA
            cor = '#9ca3af';
            desabilitado = true;
            onClick = null;
          }
          
          return (
            <button
              key={time}
              disabled={desabilitado}
              style={{
                backgroundColor: cor,
                color: is_past ? '#6b7280' : (is_occupied ? 'white' : '#1f2937'),
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
              title={
                is_occupied 
                  ? `Ocupado - ${occupancy_info?.patient_name || 'Paciente'}`
                  : is_past 
                    ? 'Horário já passou'
                    : 'Disponível - clique para agendar'
              }
            >
              {time}
              
              {/* Botão de cancelar para slots ocupados */}
              {is_occupied && occupancy_info && (
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
                    // Simular objeto agendamento para cancelamento
                    const agendamentoMock = {
                      id: occupancy_info.appointment_id,
                      patient_name: occupancy_info.patient_name
                    };
                    onCancelarAgendamento(agendamentoMock);
                    // Recarregar slots após cancelamento
                    setTimeout(recarregarSlots, 1000);
                  }}
                  title={`Cancelar agendamento de ${occupancy_info.patient_name}`}
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
});

export default ConsultorioSlots;