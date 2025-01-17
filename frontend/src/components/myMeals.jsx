import React from 'react';
import symbol from './images/bazy zdjecie.png';
import './myMeals.css';

function MyMeals() {
    return (
        <div className="mealsComponent">
            <div className="mealsContainer">
                <h1 className="mealsHeader">MOJE POSIŁKI</h1>
                <input 
                    className="searchInput" 
                    type="text" 
                    placeholder="Wyszukaj posiłek..." 
                />
                <div className="buttonContainer">
                    <button className="addMealButton">DODAJ POSIŁEK</button>
                    <button className="deleteMealButton">USUŃ POSIŁEK</button>
                </div>
            </div>

        </div>
    );
}

export default MyMeals;
