import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import './App.css';
import Login from './components/login';
import Register from './components/register';
import MyMeals from './components/myMeals';
import NewMeal from './components/newMeal';
import UserData from './components/userData';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/my-meals" element={<MyMeals />} />
                    <Route path="/new-meal" element={<NewMeal />} />
                    <Route path="/user-data" element={<UserData />} />
                    <Route path="/" element={<Navigate to="/login" />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
