import symbol from './images/bazy zdjecie.png';
import './userData.css';

function UserData() {

return (
    <div className="userDataComponent">
       <div className="userDataContainer">

            <h1 className='formHeader'>WYPEŁNIJ DANE UŻYTKOWNIKA</h1>
      
            <form>
                <label>
                    <p className="formLabel">Wiek</p>
                    <input className="formInput" type="number" />
                </label>
                <label>
                    <p className="formLabel">Wzrost (cm)</p>
                    <input className="formInput" type="number" />
                </label>
                <label>
                    <p className="formLabel">Waga (kg)</p>
                    <input className="formInput" type="number" />
                </label>
                <label>
                    <p className="formLabel">Płeć</p>
                    <select className="formInput">
                        <option value="male">Mężczyzna</option>
                        <option value="female">Kobieta</option>
                    </select>
                </label>
                <h1 className='formHeader'>Wskaż swoje cele</h1>

                  <label>
                    <p className="goalLabel">Kcal</p>
                    <input className="goalInput" type="number" />
                </label>
                <label>
                    <p className="goalLabel">Białka (g)</p>
                    <input className="goalInput" type="number" />
                </label>
                <label>
                    <p className="goalLabel">Tłuszcze (g)</p>
                    <input className="goalInput" type="number" />
                </label>
                <label>
                    <p className="goalLabel">Węglowodany (g)</p>
                    <input className="goalInput" type="number" />
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

export default UserData;