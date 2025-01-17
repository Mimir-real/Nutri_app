import symbol from './images/bazy zdjecie.png';
import './register.css';

function Register() {

return (
    <div className="loginComponent">
        <img className='symbolImage' src={symbol} alt="symbol" />
        <div className="loginContainer">

            <h1 className='formHeader'>REJESTRACJA</h1>
      
            <form>
                <label>
                    <p className="formLabel">Adres e-mail</p>
                    <input className="formInput" type="text" />
                </label>
                <label>
                    <p className="formLabel" >Hasło</p>
                    <input className="formInput" type="password" />
                </label>
                <label>
                    <p className="formLabel" >Powtórz hasło</p>
                    <input className="formInput" type="password" />
                </label>
                <div className='buttonContainter'>
                    <button className='loginButton' type="submit">UTWÓRZ KONTO</button>
                    <button className='registerButton' type="submit">POWRÓT</button>
                </div>
                </form>
        </div>

    </div>
)

}

export default Register;