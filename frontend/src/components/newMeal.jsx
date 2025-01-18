import './newMeal.css';

function NewMeal(){

return (
    <div className="newMealComponent">
        <div className="newMealContainer">
            <h1 className='mealHeader'>NOWY POSIŁEK</h1>
            <input 
            className='searchforMeal'
            type="text"
            placeholder="Nazwa posiłku..."
            />
             <input 
            className='searchforProduct'
            type="text"
            placeholder="Wyszukaj produkt..."
            />
              <div className="buttonContainer">
                    <button className="addMealButton">DODAJ POSIŁEK</button>
                    <button className="deleteMealButton">USUŃ POSIŁEK</button>
                </div>
        </div>   
    </div>
)

}

export default NewMeal;