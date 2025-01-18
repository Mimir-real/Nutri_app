import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import symbol from './images/bazy zdjecie.png';
import './login.css';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const response = await axios.post('http://localhost:5000/login', {
                email,
                password
            });
            const { access_token } = response.data;
            localStorage.setItem('token', access_token);
            console.log(response.data);
            // Redirect to MyMeals component
            navigate('/my-meals');
        } catch (error) {
            setError('Invalid email or password');
            console.error(error);
        }
    };

    return (
        <div className="loginComponent">
            <img className='symbolImage' src={symbol} alt="symbol" />
            <div className="loginContainer">
                <h1 className='formHeader'>LOGOWANIE</h1>
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
                    {error && <p className="error">{error}</p>}
                    <a href="#" className="forgotPassword">Zapomniałeś hasła?</a>
                    <div className='buttonContainter'>
                        <button className='loginButton' type="submit">ZALOGUJ SIĘ</button>
                        <button className='registerButton' type="button" onClick={() => navigate('/register')}>UTWÓRZ KONTO</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default Login;