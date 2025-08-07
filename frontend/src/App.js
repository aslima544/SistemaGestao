import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, 
  Calendar, 
  UserPlus, 
  Activity, 
  Plus,
  Eye,
  Edit,
  Trash2,
  LogOut,
  User,
  Stethoscope,
  ClipboardList
} from 'lucide-react';
import './App.css';
import ConsultorioSlots from './components/ConsultorioSlots';
import horariosConsultorios from './constants/horariosConsultorios';


function ModalAgendamento({ aberto, consultorio, horario, pacientes, doctors, procedimentos, dataSelecionada, onClose, onSubmit }) {
  const [pacienteId, setPacienteId] = useState('');
  const [doctorId, setDoctorId] = useState('');
  const [procedimentoId, setProcedimentoId] = useState('');
  const [dataAtendimento, setDataAtendimento] = useState(dataSelecionada || new Date().toISOString().slice(0,10));
  const [duration, setDuration] = useState(30);

  // Atualiza a data quando dataSelecionada muda
  React.useEffect(() => {
    setDataAtendimento(dataSelecionada || new Date().toISOString().slice(0,10));
  }, [dataSelecionada]);

  const coresProcedimentos = [
  '#fbbf24', // amarelo
  '#60a5fa', // azul
  '#34d399', // verde
  '#f87171', // vermelho
  '#a78bfa', // roxo
  '#f472b6', // rosa
  '#facc15', // amarelo ouro
  '#38bdf8', // azul claro
  '#4ade80', // verde claro
  '#fca5a5', // vermelho claro
  '#c084fc', // lilás
  '#fdba74', // laranja claro
  '#a3e635', // verde limão
  '#fcd34d', // amarelo pastel
  '#818cf8', // azul violeta
  '#f9a8d4', // rosa claro
  '#fbb6ce', // rosa bebê
  '#bef264', // verde limão claro
  '#fef08a', // amarelo claro
  '#a1a1aa', // cinza
];

  if (!aberto) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full">
        <h2 className="text-lg font-bold mb-4">
          Agendar em {consultorio?.name || ''} às {horario}
        </h2>
        <form
          onSubmit={e => {
            e.preventDefault();
            onSubmit({
              patient_id: pacienteId,
              doctor_id: doctorId,
              consultorio_id: consultorio?.id,
              dataAtendimento,
              duration,
              procedimentoId
            });
            setPacienteId('');
            setDoctorId('');
            setProcedimentoId('');
            setDataAtendimento(new Date().toISOString().slice(0,10)); // <-- adicione esta linha
            setDuration(30);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700">Data</label>
            <input
              type="date"
              className="input-field mt-1"
              value={dataAtendimento}
              onChange={e => setDataAtendimento(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Paciente</label>
            <select
              className="input-field mt-1"
              value={pacienteId}
              onChange={e => setPacienteId(e.target.value)}
              required
            >
              <option value="">Selecione um paciente</option>
              {pacientes.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Médico</label>
            <select
              className="input-field mt-1"
              value={doctorId}
              onChange={e => setDoctorId(e.target.value)}
              required
            >
              <option value="">Selecione um médico</option>
              {doctors.map(d => (
                <option key={d.id} value={d.id}>{d.name} - {d.specialty}</option>
              ))}
            </select>
          </div>
          
          <div>
              <label className="block text-sm font-medium text-gray-700">Procedimento</label>
              <select
                className="input-field mt-1"
                value={procedimentoId}
                onChange={e => setProcedimentoId(e.target.value)}
                required
              >
                <option value="">Selecione um procedimento</option>
                  {procedimentos && procedimentos.map((p, idx) => (
                    <option
                      key={p.id} value={p.id}
                      
                    >
                      {p.nome}
                    </option>
                  ))}
              </select>
            </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Duração (minutos)</label>
            <select
              className="input-field mt-1"
              value={duration}
              onChange={e => setDuration(Number(e.target.value))}
              required
            >
              <option value={15}>15</option>
              <option value={30}>30</option>
              <option value={45}>45</option>
              <option value={60}>60</option>
            </select>
          </div>
          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              Agendar
            </button>
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

// Axios configuration
axios.defaults.baseURL = API_BASE_URL;

const App = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false); 
  
  // Data states
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [consultorios, setConsultorios] = useState([]);
  const [users, setUsers] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({});
  const [weeklySchedule, setWeeklySchedule] = useState({});
  const [procedimentos, setProcedimentos] = useState([]);
  const [dataSelecionada, setDataSelecionada] = useState(new Date().toISOString().slice(0, 10));
  
  
  // Form states
  const [showPatientForm, setShowPatientForm] = useState(false);
  const [showDoctorForm, setShowDoctorForm] = useState(false);
  const [showConsultorioForm, setShowConsultorioForm] = useState(false);
  const [showUserForm, setShowUserForm] = useState(false);
  const [showAppointmentForm, setShowAppointmentForm] = useState(false);
  const [editingPatient, setEditingPatient] = useState(null);
  const [editingDoctor, setEditingDoctor] = useState(null);
  const [editingConsultorio, setEditingConsultorio] = useState(null);
  const [editingUser, setEditingUser] = useState(null);

  // Estados para slots dos consultórios
  const [consultorioSelecionado, setConsultorioSelecionado] = useState(null);
  const [agendamentos, setAgendamentos] = useState([]);

  // Estado do modal de agendamento
  const [modalAgendamento, setModalAgendamento] = useState({
    aberto: false,
    consultorio: null,
    horario: null,
  });
  
  // Set auth token
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    }
  }, [token]);

  // Buscar procedimentos ao abrir o app
  useEffect(() => {
    fetchProcedimentos();
  }, []);

  // Buscar procedimentos ao abrir o modal de agendamento
  useEffect(() => {
    if (modalAgendamento.aberto) {
      fetchProcedimentos();
    }
  }, [modalAgendamento.aberto]);

  // Buscar agendamentos ao abrir a tela
  useEffect(() => {
    axios.get('/api/appointments')
      .then(res => {
        const ags = res.data.map(a => {
          const dt = new Date(a.appointment_date);
          return {
            ...a,
            horario: dt.toTimeString().slice(0,5),
            data: dt.toISOString().slice(0,10),
            duration: a.duration_minutes || 30,
          };
        });
        setAgendamentos(ags);
      })
      .catch(err => {
        if (err.response && err.response.status === 401) {
          // Aqui você pode deslogar o usuário, redirecionar para login, etc.
          // Exemplo:
          handleLogout(); // se você já tem essa função no seu App
          alert('Sua sessão expirou. Faça login novamente.');
        } else {
          console.error('Erro ao buscar agendamentos:', err);
          setAgendamentos([]);
        }
      });
  }, [consultorioSelecionado]);

  
  // Fetch current user
  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/api/auth/me');
      setCurrentUser(response.data);
      fetchDashboardData();
    } catch (error) {
      console.error('Error fetching user:', error);
      handleLogout();
    }
  };

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, patientsRes, doctorsRes, consultoriosRes, usersRes, appointmentsRes, weeklyRes] = await Promise.all([
        axios.get('/api/dashboard/stats'),
        axios.get('/api/patients'),
        axios.get('/api/doctors'),
        axios.get('/api/consultorios'),
        axios.get('/api/users'),
        axios.get('/api/appointments'),
        axios.get('/api/consultorios/weekly-schedule')
      ]);
      
      setDashboardStats(statsRes.data);
      setPatients(patientsRes.data);
      setDoctors(doctorsRes.data);
      setConsultorios(consultoriosRes.data);
      setUsers(usersRes.data);
      setAppointments(appointmentsRes.data);
      setWeeklySchedule(weeklyRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchProcedimentos = async () => {
    try {
      const res = await axios.get('/api/procedimentos');
      setProcedimentos(res.data);
    } catch (err) {
      console.error('Erro ao buscar procedimentos:', err);
    }
  };
 
  // Login function
  const handleLogin = async (username, password) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/auth/login', { username, password });
      const { access_token } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchCurrentUser();
    } catch (error) {
      console.error('Login error:', error);
      alert('Erro no login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setCurrentUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  // Patient CRUD operations
  const handleCreatePatient = async (patientData) => {
    try {
      setLoading(true);
      await axios.post('/api/patients', patientData);
      setShowPatientForm(false);
      fetchDashboardData();
      alert('Paciente criado com sucesso!');
    } catch (error) {
      console.error('Error creating patient:', error);
      alert('Erro ao criar paciente.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePatient = async (patientId, patientData) => {
    try {
      setLoading(true);
      await axios.put(`/api/patients/${patientId}`, patientData);
      setEditingPatient(null);
      fetchDashboardData();
      alert('Paciente atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating patient:', error);
      alert('Erro ao atualizar paciente.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePatient = async (patientId) => {
    if (window.confirm('Tem certeza que deseja excluir este paciente?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/patients/${patientId}`);
        fetchDashboardData();
        alert('Paciente excluído com sucesso!');
      } catch (error) {
        console.error('Error deleting patient:', error);
        alert('Erro ao excluir paciente.');
      } finally {
        setLoading(false);
      }
    }
  };

  // User CRUD operations
  const handleCreateUser = async (userData) => {
    try {
      setLoading(true);
      await axios.post('/api/users', userData);
      setShowUserForm(false);
      fetchDashboardData();
      alert('Usuário criado com sucesso!');
    } catch (error) {
      console.error('Error creating user:', error);
      if (error.response?.status === 400) {
        alert('Erro: Nome de usuário já existe.');
      } else {
        alert('Erro ao criar usuário.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId, userData) => {
    try {
      setLoading(true);
      await axios.put(`/api/users/${userId}`, userData);
      setEditingUser(null);
      fetchDashboardData();
      alert('Usuário atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating user:', error);
      alert('Erro ao atualizar usuário.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('Tem certeza que deseja excluir este usuário?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/users/${userId}`);
        fetchDashboardData();
        alert('Usuário excluído com sucesso!');
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Erro ao excluir usuário.');
      } finally {
        setLoading(false);
      }
    }
  };

  // Consultorio CRUD operations
  const handleCreateConsultorio = async (consultorioData) => {
    try {
      setLoading(true);
      await axios.post('/api/consultorios', consultorioData);
      setShowConsultorioForm(false);
      fetchDashboardData();
      alert('Consultório criado com sucesso!');
    } catch (error) {
      console.error('Error creating consultorio:', error);
      alert('Erro ao criar consultório.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateConsultorio = async (consultorioId, consultorioData) => {
    try {
      setLoading(true);
      await axios.put(`/api/consultorios/${consultorioId}`, consultorioData);
      setEditingConsultorio(null);
      fetchDashboardData();
      alert('Consultório atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating consultorio:', error);
      alert('Erro ao atualizar consultório.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConsultorio = async (consultorioId) => {
    if (window.confirm('Tem certeza que deseja excluir este consultório?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/consultorios/${consultorioId}`);
        fetchDashboardData();
        alert('Consultório excluído com sucesso!');
      } catch (error) {
        console.error('Error deleting consultorio:', error);
        alert('Erro ao excluir consultório.');
      } finally {
        setLoading(false);
      }
    }
  };

  // Doctor CRUD operations
  const handleCreateDoctor = async (doctorData) => {
    try {
      setLoading(true);
      await axios.post('/api/doctors', doctorData);
      setShowDoctorForm(false);
      fetchDashboardData();
      alert('Médico criado com sucesso!');
    } catch (error) {
      console.error('Error creating doctor:', error);
      alert('Erro ao criar médico.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDoctor = async (doctorId, doctorData) => {
    try {
      setLoading(true);
      await axios.put(`/api/doctors/${doctorId}`, doctorData);
      setEditingDoctor(null);
      fetchDashboardData();
      alert('Médico atualizado com sucesso!');
    } catch (error) {
      console.error('Error updating doctor:', error);
      alert('Erro ao atualizar médico.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDoctor = async (doctorId) => {
    if (window.confirm('Tem certeza que deseja excluir este médico?')) {
      try {
        setLoading(true);
        await axios.delete(`/api/doctors/${doctorId}`);                
        await fetchDashboardData();        
        alert('Médico excluído com sucesso!');
      } catch (error) {
        console.error('Error deleting doctor:', error);
        alert('Erro ao excluir médico.');
      } finally {
        setLoading(false);
      }
    }
  };

  // Appointment CRUD operations
  const handleCreateAppointment = async (appointmentData) => {
    try {
      setLoading(true);
      await axios.post('/api/appointments', appointmentData);
      setShowAppointmentForm(false);
      
      // Update both states for immediate UI refresh
      await fetchDashboardData(); // Updates appointments state
      const agendamentosRes = await axios.get('/api/appointments');
      
      // Process agendamentos data with same format as useEffect
      const ags = agendamentosRes.data.map(a => {
        const dt = new Date(a.appointment_date);
        return {
          ...a,
          horario: dt.toTimeString().slice(0,5),
          data: dt.toISOString().slice(0,10),
          duration: a.duration_minutes || 30,
        };
      });
      setAgendamentos(ags); // Updates agendamentos state for slots with proper format
      
      alert('Consulta agendada com sucesso!');
    } catch (error) {
      console.error('Error creating appointment:', error);
      alert('Erro ao agendar consulta.');
    } finally {
      setLoading(false);
    }
  };

  const onCancelarAgendamento = async (agendamento) => {
  if (window.confirm("Deseja liberar este horário?")) {
    try {
      await axios.put(`/api/appointments/${agendamento.id}/cancel`);
      // Atualize os agendamentos após cancelar com formato consistente
      const res = await axios.get('/api/appointments');
      const ags = res.data.map(a => {
        const dt = new Date(a.appointment_date);
        return {
          ...a,
          horario: dt.toTimeString().slice(0,5),
          data: dt.toISOString().slice(0,10),
          duration: a.duration_minutes || 30,
        };
      });
      setAgendamentos(ags);
      // Atualize o dashboard também
      fetchDashboardData();
    } catch (err) {
      alert('Erro ao liberar horário!');
      console.error(err);
    }
  }
};


  // Login Component
  const LoginForm = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const onSubmit = (e) => {
      e.preventDefault();
      handleLogin(username, password);
    };
       

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
        <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
          <div className="text-center">
            <Stethoscope className="mx-auto h-12 w-12 text-primary-600" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Sistema de Gestão
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Entre com suas credenciais
            </p>
          </div>
          <form className="mt-8 space-y-6" onSubmit={onSubmit}>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Usuário
              </label>
              <input
                type="text"
                required
                className="input-field mt-1"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Senha
              </label>
              <input
                type="password"
                required
                className="input-field mt-1"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua senha"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
          {/*<div className="text-center text-sm text-gray-600">
           <p>Usuário padrão: <strong>admin</strong></p>
            <p>Senha padrão: <strong>admin123</strong></p>
          </div>*/}
        </div>
      </div>
    );
  };

  // Patient Form Component
  const PatientForm = ({ patient, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      name: patient?.name || '',
      email: patient?.email || '',
      phone: patient?.phone || '',
      cpf: patient?.cpf || '',
      birth_date: patient?.birth_date?.split('T')[0] || '',
      address: patient?.address || '',
      medical_history: patient?.medical_history || ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const submitData = {
        ...formData,
        birth_date: new Date(formData.birth_date).toISOString()
      };
      onSubmit(submitData);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {patient ? 'Editar Paciente' : 'Novo Paciente'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="input-field mt-1"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Telefone</label>
                <input
                  type="tel"
                  required
                  className="input-field mt-1"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">CPF</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.cpf}
                  onChange={(e) => setFormData({ ...formData, cpf: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Data de Nascimento</label>
                <input
                  type="date"
                  required
                  className="input-field mt-1"
                  value={formData.birth_date}
                  onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Endereço</label>
                <textarea
                  className="input-field mt-1"
                  rows="2"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Histórico Médico</label>
                <textarea
                  className="input-field mt-1"
                  rows="3"
                  value={formData.medical_history}
                  onChange={(e) => setFormData({ ...formData, medical_history: e.target.value })}
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  {patient ? 'Atualizar' : 'Criar'}
                </button>
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

// Doctor Form Component
  const DoctorForm = ({ doctor, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      name: doctor?.name || '',
      email: doctor?.email || '',
      phone: doctor?.phone || '',
      crm: doctor?.crm || '',
      specialty: doctor?.specialty || ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {doctor ? 'Editar Médico' : 'Novo Médico'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  required
                  className="input-field mt-1"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Telefone</label>
                <input
                  type="tel"
                  required
                  className="input-field mt-1"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">CRM</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.crm}
                  onChange={(e) => setFormData({ ...formData, crm: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Especialidade</label>
                <select
                  required
                  className="input-field mt-1"
                  value={formData.specialty}
                  onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
                >
                  <option value="">Selecione uma especialidade</option>
                  <option value="Cardiologia">Cardiologia</option>
                  <option value="Dermatologia">Dermatologia</option>
                  <option value="Pediatria">Pediatria</option>
                  <option value="Ortopedia">Ortopedia</option>
                  <option value="Neurologia">Neurologia</option>
                  <option value="Ginecologia">Ginecologia</option>
                  <option value="Clínico Geral">Clínico Geral</option>
                </select>
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  {doctor ? 'Atualizar' : 'Criar'}
                </button>
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // User Form Component
  const UserForm = ({ user, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      username: user?.username || '',
      email: user?.email || '',
      full_name: user?.full_name || '',
      role: user?.role || 'reception',
      password: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!user && !formData.password) {
        alert('Senha é obrigatória para novos usuários');
        return;
      }
      onSubmit(formData);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {user ? 'Editar Usuário' : 'Novo Usuário'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome de Usuário</label>
                <input
                  type="text"
                  required
                  disabled={!!user} // Disable editing username for existing users
                  className={`input-field mt-1 ${user ? 'bg-gray-100' : ''}`}
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  placeholder="Ex: joao.silva"
                />
                {user && (
                  <p className="text-xs text-gray-500 mt-1">Nome de usuário não pode ser alterado</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome Completo</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  placeholder="Ex: João Silva Santos"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  required
                  className="input-field mt-1"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="Ex: joao.silva@email.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Função</label>
                <select
                  required
                  className="input-field mt-1"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                >
                  <option value="reception">Recepção</option>
                  <option value="doctor">Médico</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  {user ? 'Nova Senha (deixe em branco para não alterar)' : 'Senha'}
                </label>
                <input
                  type="password"
                  required={!user}
                  className="input-field mt-1"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder={user ? 'Digite nova senha para alterar' : 'Digite a senha'}
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  {user ? 'Atualizar' : 'Criar'}
                </button>
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

   // Consultorio Form Component
  const ConsultorioForm = ({ consultorio, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      name: consultorio?.name || '',
      description: consultorio?.description || '',
      capacity: consultorio?.capacity || 1,
      equipment: consultorio?.equipment?.join(', ') || '',
      location: consultorio?.location || ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const submitData = {
        ...formData,
        equipment: formData.equipment.split(',').map(item => item.trim()).filter(item => item)
      };
      onSubmit(submitData);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {consultorio ? 'Editar Consultório' : 'Novo Consultório'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome</label>
                <input
                  type="text"
                  required
                  className="input-field mt-1"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Ex: Consultório 1, Sala A"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Descrição</label>
                <textarea
                  className="input-field mt-1"
                  rows="2"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Descrição do consultório"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Capacidade</label>
                <select
                  className="input-field mt-1"
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: parseInt(e.target.value) })}
                >
                  <option value={1}>1 pessoa</option>
                  <option value={2}>2 pessoas</option>
                  <option value={3}>3 pessoas</option>
                  <option value={4}>4 pessoas</option>
                  <option value={5}>5+ pessoas</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Equipamentos</label>
                <input
                  type="text"
                  className="input-field mt-1"
                  value={formData.equipment}
                  onChange={(e) => setFormData({ ...formData, equipment: e.target.value })}
                  placeholder="Ex: Estetoscópio, Otoscópio, Balança (separados por vírgula)"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Localização</label>
                <input
                  type="text"
                  className="input-field mt-1"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  placeholder="Ex: 1º andar, Ala Norte"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  {consultorio ? 'Atualizar' : 'Criar'}
                </button>
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Appointment Form Component
  const AppointmentForm = ({ appointment, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      patient_id: appointment?.patient_id || '',
      doctor_id: appointment?.doctor_id || '',
      consultorio_id: appointment?.consultorio_id || '',
      appointment_date: appointment?.appointment_date?.slice(0, 16) || '',
      duration_minutes: appointment?.duration_minutes || 30,
      notes: appointment?.notes || ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      const submitData = {
        ...formData,
        appointment_date: new Date(formData.appointment_date).toISOString()
      };
      onSubmit(submitData);
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg max-w-md w-full">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Nova Consulta
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Paciente</label>
                <select
                  required
                  className="input-field mt-1"
                  value={formData.patient_id}
                  onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                >
                  <option value="">Selecione um paciente</option>
                  {patients.map(patient => (
                    <option key={patient.id} value={patient.id}>
                      {patient.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Médico</label>
                <select
                  required
                  className="input-field mt-1"
                  value={formData.doctor_id}
                  onChange={(e) => setFormData({ ...formData, doctor_id: e.target.value })}
                >
                  <option value="">Selecione um médico</option>
                  {doctors.map(doctor => (
                    <option key={doctor.id} value={doctor.id}>
                      {doctor.name} - {doctor.specialty}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Consultório</label>
                <select
                  required
                  className="input-field mt-1"
                  value={formData.consultorio_id}
                  onChange={(e) => setFormData({ ...formData, consultorio_id: e.target.value })}
                >
                  <option value="">Selecione um consultório</option>
                  {consultorios.map(consultorio => (
                    <option key={consultorio.id} value={consultorio.id}>
                      {consultorio.name} - {consultorio.location || 'Sem localização'}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Data e Hora</label>
                <input
                  type="datetime-local"
                  required
                  className="input-field mt-1"
                  value={formData.appointment_date}
                  onChange={(e) => setFormData({ ...formData, appointment_date: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Duração (minutos)</label>
                <select
                  className="input-field mt-1"
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                >
                  <option value={15}>15 minutos</option>
                  <option value={30}>30 minutos</option>
                  <option value={45}>45 minutos</option>
                  <option value={60}>60 minutos</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Observações</label>
                <textarea
                  className="input-field mt-1"
                  rows="3"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">
                  Agendar
                </button>
                <button type="button" onClick={onCancel} className="btn-secondary flex-1">
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Dashboard Component
  const Dashboard = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-600">
          Bem-vindo, {currentUser?.full_name}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Total Pacientes</div>
              <div className="text-2xl font-bold text-gray-900">
                {dashboardStats.total_patients || 0}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Stethoscope className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Total Médicos</div>
              <div className="text-2xl font-bold text-gray-900">
                {dashboardStats.total_doctors || 0}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-orange-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Total Consultórios</div>
              <div className="text-2xl font-bold text-gray-900">
                {dashboardStats.total_consultorios || 0}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Activity className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <div className="text-sm font-medium text-gray-500">Consultas Hoje</div>
              <div className="text-2xl font-bold text-gray-900">
                {dashboardStats.today_appointments || 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Consultorio Occupancy */}
      {dashboardStats.consultorio_stats && dashboardStats.consultorio_stats.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Ocupação dos Consultórios Hoje</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {dashboardStats.consultorio_stats.map((consultorio) => (
              <div key={consultorio.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-900">{consultorio.name}</span>
                  <span className="text-sm font-medium text-primary-600">
                    {consultorio.occupied_slots} consultas
                  </span>
                </div>
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-primary-600 h-2 rounded-full" 
                      style={{width: `${Math.min(100, (consultorio.occupied_slots / 8) * 100)}%`}}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mapa de Salas - Fixed Schedule */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">📌 Consultórios Fixos (ESF)</h2>
          <div className="space-y-3">
            {weeklySchedule.fixed_consultorios?.map((consultorio) => (
              <div key={consultorio.id} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {consultorio.name}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{consultorio.team}</div>
                    <div className="text-sm text-gray-600">{consultorio.location}</div>
                  </div>
                </div>
                <div className="text-sm font-medium text-blue-700">
                  {consultorio.schedule}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">🔄 Consultórios Rotativos</h2>
          <div className="space-y-3">
            {weeklySchedule.rotative_consultorios?.map((consultorio) => (
              <div key={consultorio.id} className="flex items-center justify-between p-3 bg-orange-50 rounded-lg border border-orange-200">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                    {consultorio.name}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{consultorio.description}</div>
                    <div className="text-sm text-gray-600">{consultorio.location}</div>
                  </div>
                </div>
                <div className="text-xs text-orange-700 bg-orange-100 px-2 py-1 rounded">
                  Uso Variável
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cronograma Semanal */}
      {weeklySchedule.schedule_grid && Object.keys(weeklySchedule.schedule_grid).length > 0 && (
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">🗓️ Cronograma Semanal (Consultórios Rotativos)</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Consultório</th>
                  <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Segunda</th>
                  <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Terça</th>
                  <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Quarta</th>
                  <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Quinta</th>
                  <th className="px-4 py-2 text-center text-sm font-medium text-gray-700">Sexta</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {Object.entries(weeklySchedule.schedule_grid).map(([consultorioName, schedule]) => (
                  <tr key={consultorioName} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{consultorioName}</td>
                    {['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta'].map((day) => (
                      <td key={day} className="px-4 py-3 text-center">
                        <div className="space-y-1">
                          <div className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                            M: {schedule[day]?.morning || 'Livre'}
                          </div>
                          <div className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            T: {schedule[day]?.afternoon || 'Livre'}
                          </div>
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-4 text-xs text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-100 rounded"></div>
              <span>M = Manhã</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-100 rounded"></div>
              <span>T = Tarde</span>
            </div>
            <div className="text-sm text-gray-500 ml-4">
              📝 Visita Domiciliar: Segunda e Quarta (ESF parcialmente liberado)
            </div>
          </div>
        </div>
      )}

      {/* Recent Appointments */}
      <div className="card">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900">Consultas Recentes</h2>
          <button
            onClick={() => setShowAppointmentForm(true)}
            className="btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nova Consulta
          </button>
        </div>
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Paciente
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Médico
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Consultório
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Data/Hora
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboardStats.recent_appointments?.map((appointment) => (
                <tr key={appointment.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {appointment.patient_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {appointment.doctor_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {appointment.consultorio_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(appointment.appointment_date).toLocaleString('pt-BR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      appointment.status === 'scheduled' 
                        ? 'bg-blue-100 text-blue-800' 
                        : appointment.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {appointment.status === 'scheduled' ? 'Agendado' : 
                       appointment.status === 'completed' ? 'Concluído' : 'Cancelado'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // Patients Component
  const PatientsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Pacientes</h1>
        <button
          onClick={() => setShowPatientForm(true)}
          className="btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Paciente
        </button>
      </div>

      <div className="card">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Telefone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CPF
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {patients.map((patient) => (
                <tr key={patient.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {patient.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.email || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.cpf}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setEditingPatient(patient)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeletePatient(patient.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // DoctorsTab (corrigido)
  const DoctorsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Médicos</h1>
        <button
          onClick={() => setShowDoctorForm(true)}
          className="btn-primary"
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Médico
        </button>
      </div>

      <div className="card">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CRM
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Especialidade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Telefone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {doctors.map((doctor) => (
                <tr key={doctor.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {doctor.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doctor.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doctor.crm}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doctor.specialty}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {doctor.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => setEditingDoctor(doctor)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteDoctor(doctor.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

 const ConsultoriosTab = () => (
  <div className="space-y-6">
    <div className="flex justify-between items-center">
      <h1 className="text-2xl font-bold text-gray-900">Consultórios & Mapa de Salas</h1>
      <button
        onClick={() => setShowConsultorioForm(true)}
        className="btn-primary"
      >
        <Plus className="h-4 w-4 mr-2" />
        Novo Consultório
      </button>
    </div>

    {/* Campo para selecionar a data */}
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700">Data:</label>
      <input
        type="date"
        className="input-field mt-1"
        value={dataSelecionada}
        onChange={e => setDataSelecionada(e.target.value)}
      />
    </div>

    {/* Lista de consultórios fixos com botão para ver horários */}
    <div className="card">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Consultórios Fixos</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {consultorios.map(c => (
          <div key={c.id} className="p-4 border rounded">
            <div className="font-bold">{c.name}</div>
            <div>
              {c.fixed_schedule
                ? `${c.fixed_schedule.start} - ${c.fixed_schedule.end}`
                : '07:00 - 19:00'}
            </div>
            <button
              className="btn-primary mt-2"
              onClick={() => setConsultorioSelecionado(c.id)}
            >
              Ver horários
            </button>
          </div>
        ))}
      </div>
    </div>

    {/* Exibe os slots do consultório selecionado */}
    {consultorioSelecionado && (
      <div className="mt-6">
        <h3 className="text-lg font-bold mb-2">
          Horários do {
            (consultorios.find(c => c.id === consultorioSelecionado) || {}).name
          }
          <button
            className="ml-4 text-sm text-blue-600 underline"
            onClick={() => setConsultorioSelecionado(null)}
          >
            Fechar
          </button>
        </h3>
        <ConsultorioSlots
          consultorio={consultorios.find(c => c.id === consultorioSelecionado)}
          agendamentos={agendamentos}
          dataSelecionada={dataSelecionada} // <-- aqui está a data!
          onAgendar={horario =>
            setModalAgendamento({
              aberto: true,
              consultorio: consultorios.find(c => c.id === consultorioSelecionado),
              horario
            })
          }
          onCancelarAgendamento={onCancelarAgendamento}
        />
      </div>
    )}
  </div>
);

   // Users Component
  const UsersTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Gerenciar Usuários</h1>
        <button
          onClick={() => setShowUserForm(true)}
          className="btn-primary"
          disabled={currentUser?.role !== 'admin'}
        >
          <Plus className="h-4 w-4 mr-2" />
          Novo Usuário
        </button>
      </div>

      {currentUser?.role !== 'admin' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <User className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-800">
                Apenas administradores podem gerenciar usuários do sistema.
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Usuário
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nome Completo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Função
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Criado em
                </th>
                {currentUser?.role === 'admin' && (
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ações
                  </th>
                )}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className={user.id === currentUser?.id ? 'bg-blue-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold mr-3 ${
                        user.role === 'admin' ? 'bg-red-500' : 
                        user.role === 'doctor' ? 'bg-green-500' : 'bg-blue-500'
                      }`}>
                        {user.role === 'admin' ? 'A' : user.role === 'doctor' ? 'M' : 'R'}
                      </div>
                      <div className="text-sm font-medium text-gray-900">
                        {user.username}
                        {user.id === currentUser?.id && (
                          <span className="ml-2 text-xs text-blue-600 font-medium">(Você)</span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {user.full_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.role === 'admin' ? 'bg-red-100 text-red-800' :
                      user.role === 'doctor' ? 'bg-green-100 text-green-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {user.role === 'admin' ? 'Administrador' :
                       user.role === 'doctor' ? 'Médico' : 'Recepção'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {user.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.created_at ? new Date(user.created_at).toLocaleDateString('pt-BR') : '-'}
                  </td>
                  {currentUser?.role === 'admin' && (
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setEditingUser(user)}
                          className="text-primary-600 hover:text-primary-900"
                          disabled={user.id === currentUser?.id}
                        >
                          <Edit className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                          disabled={user.id === currentUser?.id || user.role === 'admin'}
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              A
            </div>
            <div>
              <div className="text-sm font-medium text-red-800">Administradores</div>
              <div className="text-xs text-red-600">Acesso completo ao sistema</div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              M
            </div>
            <div>
              <div className="text-sm font-medium text-green-800">Médicos</div>
              <div className="text-xs text-green-600">Acesso a consultas e pacientes</div>
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              R
            </div>
            <div>
              <div className="text-sm font-medium text-blue-800">Recepção</div>
              <div className="text-xs text-blue-600">Agendamentos e cadastros</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const ProceduresTab = () => {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ nome: '', descricao: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editing) {
        await axios.put(`/api/procedimentos/${editing.id}`, form);
      } else {
        await axios.post('/api/procedimentos', form);
      }
      setShowForm(false);
      setEditing(null);
      setForm({ nome: '', descricao: '' });
      fetchProcedimentos();
    } catch (err) {
      alert('Erro ao salvar procedimento!');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Deseja excluir este procedimento?')) {
      await axios.delete(`/api/procedimentos/${id}`);
      fetchProcedimentos();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Procedimentos</h1>
        <button onClick={() => { setShowForm(true); setEditing(null); setForm({ nome: '', descricao: '' }); }} className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Novo Procedimento
        </button>
      </div>
      <div className="card">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {procedimentos.map((p) => (
              <tr key={p.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{p.nome}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{p.descricao || '-'}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button onClick={() => { setEditing(p); setForm({ nome: p.nome, descricao: p.descricao }); setShowForm(true); }} className="text-primary-600 hover:text-primary-900 mr-2">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button onClick={() => handleDelete(p.id)} className="text-red-600 hover:text-red-900">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-lg font-bold mb-4">{editing ? 'Editar' : 'Novo'} Procedimento</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome</label>
                <input type="text" className="input-field mt-1" value={form.nome} onChange={e => setForm({ ...form, nome: e.target.value })} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Descrição</label>
                <textarea className="input-field mt-1" value={form.descricao} onChange={e => setForm({ ...form, descricao: e.target.value })} />
              </div>
              <div className="flex space-x-3 pt-4">
                <button type="submit" className="btn-primary flex-1">{editing ? 'Atualizar' : 'Criar'}</button>
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary flex-1">Cancelar</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};


 // Main App Layout
  if (!currentUser) {
    return <LoginForm />;
  }

  return (       
   <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Stethoscope className="h-8 w-8 text-primary-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                Sistema de Gestão
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-8">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'dashboard'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Activity className="h-4 w-4 inline mr-2" />
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('patients')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'patients'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Users className="h-4 w-4 inline mr-2" />
                  Pacientes
                </button>
                <button
                  onClick={() => setActiveTab('doctors')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'doctors'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Stethoscope className="h-4 w-4 inline mr-2" />
                  Médicos
                </button>
                <button
                  onClick={() => setActiveTab('consultorios')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'consultorios'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <ClipboardList className="h-4 w-4 inline mr-2" />
                  Consultórios
                </button>

                <button
                  onClick={() => setActiveTab('procedures')}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    activeTab === 'procedures'
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <ClipboardList className="h-4 w-4 inline mr-2" />
                  Procedimentos
                </button>

                {currentUser?.role === 'admin' && (
                  <button
                    onClick={() => setActiveTab('users')}
                    className={`px-3 py-2 text-sm font-medium rounded-md ${
                      activeTab === 'users'
                        ? 'bg-primary-100 text-primary-700'
                        : 'text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <User className="h-4 w-4 inline mr-2" />
                    Usuários
                  </button>
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{currentUser.full_name}</span>
                <button
                  onClick={handleLogout}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>
      
      <main className="mx-auto max-w-7xl py-6 px-4 sm:px-6 lg:px-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'patients' && <PatientsTab />}
        {activeTab === 'doctors' && <DoctorsTab />}
        {activeTab === 'consultorios' && <ConsultoriosTab />}
        {activeTab === 'procedures' && <ProceduresTab />}
        {activeTab === 'users' && <UsersTab />}
      </main>


      <ModalAgendamento
          aberto={modalAgendamento.aberto}
          consultorio={modalAgendamento.consultorio}
          horario={modalAgendamento.horario}
          pacientes={patients}
          doctors={doctors}
          procedimentos={procedimentos}
          dataSelecionada={dataSelecionada}
          onClose={() => setModalAgendamento({ aberto: false, consultorio: null, horario: null })}
          onSubmit={async dados => {
            // Debug: vamos ver exatamente o que está acontecendo
            console.log('🐛 DEBUG AGENDAMENTO:', {
              dataAtendimento: dados.dataAtendimento,
              horario: modalAgendamento.horario,
              dataSelecionada: dataSelecionada
            });
            
            // 1. Monte a string de data/hora completa
            const dataHoraStr = `${dados.dataAtendimento}T${modalAgendamento.horario}:00`;
            console.log('🐛 dataHoraStr:', dataHoraStr);

            // 2. Crie o objeto Date
            const dataHora = new Date(dataHoraStr);
            console.log('🐛 dataHora object:', dataHora);
            console.log('🐛 dataHora.toISOString():', dataHora.toISOString());

            // 3. Valide se a data é válida
            if (isNaN(dataHora.getTime())) {
              alert('Data e horário inválidos!');
              return;
            }

            // 4. Valide se a data/hora já passou
            const agora = new Date();
            if (dataHora < agora) {
              alert('Não é possível agendar para um horário que já passou!');
              return;
            }

            try {
              await axios.post('/api/appointments', {
                patient_id: dados.patient_id,
                doctor_id: dados.doctor_id,
                consultorio_id: modalAgendamento.consultorio?.id,
                appointment_date: dataHora.toISOString(),
                duration_minutes: dados.duration,
                notes: dados.procedimentoId || ''
              });
              
              // Close modal and refresh all data immediately
              setModalAgendamento({ aberto: false, consultorio: null, horario: null });
              
              // Update both states to ensure consistency
              await fetchDashboardData(); // Updates appointments state
              const agendamentosRes = await axios.get('/api/appointments');
              
              // Process agendamentos data with same format as useEffect
              const ags = agendamentosRes.data.map(a => {
                const dt = new Date(a.appointment_date);
                return {
                  ...a,
                  horario: dt.toTimeString().slice(0,5),
                  data: dt.toISOString().slice(0,10),
                  duration: a.duration_minutes || 30,
                };
              });
              setAgendamentos(ags); // Updates agendamentos state for slots with proper format
              
              alert('Consulta agendada com sucesso!');
            } catch (err) {
              console.error('Erro ao salvar agendamento:', err);
              if (err.response && err.response.data && err.response.data.detail) {
                // Se for array, junte as mensagens
                if (Array.isArray(err.response.data.detail)) {
                  alert(
                    'Erro ao salvar agendamento:\n' +
                    err.response.data.detail.map(e =>
                      typeof e === 'string'
                        ? e
                        : (e.msg || JSON.stringify(e))
                    ).join('\n')
                  );
                } else if (typeof err.response.data.detail === 'object') {
                  alert('Erro ao salvar agendamento: ' + JSON.stringify(err.response.data.detail, null, 2));
                } else {
                  alert('Erro ao salvar agendamento: ' + err.response.data.detail);
                }
              } else if (err.message) {
                alert('Erro ao salvar agendamento: ' + err.message);
              } else {
                alert('Erro ao salvar agendamento (erro desconhecido)');
              }
            }
          }}
       />

      {/* Modals */}
      {showPatientForm && (
        <PatientForm
          onSubmit={handleCreatePatient}
          onCancel={() => setShowPatientForm(false)}
        />
      )}

      {editingPatient && (
        <PatientForm
          patient={editingPatient}
          onSubmit={(data) => handleUpdatePatient(editingPatient.id, data)}
          onCancel={() => setEditingPatient(null)}
        />
      )}

      {showUserForm && (
        <UserForm
          onSubmit={handleCreateUser}
          onCancel={() => setShowUserForm(false)}
        />
      )}

      {editingUser && (
        <UserForm
          user={editingUser}
          onSubmit={(data) => handleUpdateUser(editingUser.id, data)}
          onCancel={() => setEditingUser(null)}
        />
      )}

      {showDoctorForm && (
        <DoctorForm
          onSubmit={handleCreateDoctor}
          onCancel={() => setShowDoctorForm(false)}
        />
      )}

      {editingDoctor && (
        <DoctorForm
          doctor={editingDoctor}
          onSubmit={(data) => handleUpdateDoctor(editingDoctor.id, data)}
          onCancel={() => setEditingDoctor(null)}
        />
      )}

      {showConsultorioForm && (
        <ConsultorioForm
          onSubmit={handleCreateConsultorio}
          onCancel={() => setShowConsultorioForm(false)}
        />
      )}

      {editingConsultorio && (
        <ConsultorioForm
          consultorio={editingConsultorio}
          onSubmit={(data) => handleUpdateConsultorio(editingConsultorio.id, data)}
          onCancel={() => setEditingConsultorio(null)}
        />
      )}

      {showAppointmentForm && (
        <AppointmentForm
          onSubmit={handleCreateAppointment}
          onCancel={() => setShowAppointmentForm(false)}
        />
      )}

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;