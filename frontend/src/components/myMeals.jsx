import React, { useEffect, useState } from 'react';
import axios from './axiosConfig'; // Użyj skonfigurowanej instancji Axios
import symbol from './images/bazy zdjecie.png';
import './myMeals.css';

function MyMeals() {
    const [meals, setMeals] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchMeals = async () => {
            try {
                const response = await axios.get('/meals');
                setMeals(response.data);
            } catch (error) {
                setError('Failed to fetch meals');
                console.error(error);
            }
        };

        fetchMeals();
    }, []);

    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const filteredMeals = meals.filter(meal =>
        meal.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="mealsComponent">
            <img className='symbolImage' src={symbol} alt="symbol" />
            <div className="mealsContainer">
                <h1 className="mealsHeader">MOJE POSIŁKI</h1>
                <input 
                    className="searchInput" 
                    type="text" 
                    placeholder="Wyszukaj posiłek..." 
                    value={searchTerm}
                    onChange={handleSearchChange}
                />
                {error && <p className="error">{error}</p>}
                <ul>
                    {filteredMeals.map(meal => (
                        <li key={meal.id}>{meal.name}</li>
                    ))}
                </ul>
                <div className="buttonContainer">
                    <button className="addMealButton">DODAJ POSIŁEK</button>
                    <button className="deleteMealButton">USUŃ POSIŁEK</button>
                </div>
            </div>
        </div>
    );
}

export default MyMeals;
