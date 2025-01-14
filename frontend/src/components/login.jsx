
function Login() {

return (
    <div className="loginComponent">
        <div className="loginContainer">
            <h1>LOGOWANIE</h1>
            <form>
                <label>
                    <p>Adres e-mail</p>
                    <input type="text" />
                </label>
                <label>
                    <p>hasło</p>
                    <input type="password" />
                </label>
                <div>
                    <button type="submit">ZALOGUJ SIĘ</button>
                    <button type="submit">UTWÓRZ KONTO</button>
                </div>
                </form>
        </div>

    </div>
)

}

export default Login;