import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import symbol from './images/bazy zdjecie.png';
import './register.css';

function Register() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        try {
            const response = await axios.post('http://localhost:5000/register', {
                email,
                password
            });
            console.log(response.data);
            // Redirect to login page after successful registration
            navigate('/login');
        } catch (error) {
            setError('Registration failed');
            console.error(error);
        }
    };

    return (
        <div className="loginComponent">
            <img className='symbolImage' src={symbol} alt="symbol" />
            <div className="loginContainer">
                <h1 className='formHeader'>REJESTRACJA</h1>
                <form onSubmit={handleSubmit}>
                    <label>
                        <p className="formLabel">Adres e-mail</p>
                        <input
                            className="formInput"
                            type="text"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </label>
                    <label>
                        <p className="formLabel">Hasło</p>
                        <input
                            className="formInput"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </label>
                    <label>
                        <p className="formLabel">Powtórz hasło</p>
                        <input
                            className="formInput"
                            type="password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    </label>
                    {error && <p className="error">{error}</p>}
                    <div className='buttonContainter'>
                        <button className='loginButton' type="submit">UTWÓRZ KONTO</button>
                        <button className='registerButton' type="button" onClick={() => navigate('/login')}>POWRÓT</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Register;