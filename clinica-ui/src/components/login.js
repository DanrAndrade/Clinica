import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // O seu Django em Eunápolis rodando na porta 8000
      const response = await axios.post('http://127.0.0.1:8000/api/v1/auth/login', {
        email: email,
        password: password
      });
      alert(`Bem-vindo, ${response.data.nome_completo}!`);
    } catch (error) {
      alert("Erro ao logar: " + (error.response?.data?.detail || "Erro de conexão"));
    }
  };

  return (
    <div style={{ padding: '50px', textAlign: 'center', fontFamily: 'Arial' }}>
      <h1>Avda Software</h1>
      <form onSubmit={handleLogin} style={{ display: 'inline-block', textAlign: 'left' }}>
        <input 
          type="email" 
          placeholder="E-mail" 
          onChange={(e) => setEmail(e.target.value)} 
          style={{ display: 'block', padding: '10px', marginBottom: '10px', width: '250px' }}
        />
        <input 
          type="password" 
          placeholder="Senha" 
          onChange={(e) => setPassword(e.target.value)} 
          style={{ display: 'block', padding: '10px', marginBottom: '10px', width: '250px' }}
        />
        <button type="submit" style={{ padding: '10px', width: '100%', cursor: 'pointer' }}>
          Entrar no Sistema
        </button>
      </form>
    </div>
  );
};

export default Login;