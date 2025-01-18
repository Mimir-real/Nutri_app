import React, { useEffect, useState } from 'react';
import axios from './axiosConfig'; // Use the configured Axios instance
import symbol from './images/bazy zdjecie.png';
import './myMeals.css';

function MyMeals() {
    const [meals, setMeals] = useState([]); // Initialize as an array
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchMeals = async () => {
            try {
                const response = await axios.get('/meals');
                const data = response.data;

                // Log the actual response for debugging
                console.log('Response data:', data);

                // Check and ensure the response contains the meals array
                if (data && Array.isArray(data.meals)) {
                    setMeals(data.meals);
                } else {
                    throw new Error('Unexpected response format: meals key is not an array');
                }
            } catch (error) {
                setError('Failed to fetch meals');
                console.error('Error fetching meals:', error);
                setMeals([]); // Set meals to an empty array on error
            }
        };

        fetchMeals();
    }, []);

    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
    };

    // Safe rendering for meals
    const renderMeals = () => {
        if (!Array.isArray(meals)) return null; // Guard clause for non-array data

        return meals
            .filter(meal => meal.name && meal.name.toLowerCase().includes(searchTerm.toLowerCase()))
            .map(meal => <li key={meal.id}>{meal.name}</li>);
    };

    return (
        <div className="mealsComponent" >

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
                <ul>{renderMeals()}</ul>
                <div className="buttonContainer">
                    <button className="addMealButton">DODAJ POSIŁEK</button>
                    <button className="deleteMealButton">USUŃ POSIŁEK</button>
                </div>
            </div>
        </div>
    );
}

export default MyMeals;
