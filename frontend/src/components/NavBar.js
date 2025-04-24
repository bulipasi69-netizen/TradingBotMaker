// src/components/NavBar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';

export default function NavBar() {
  const base  = 'text-gray-600 hover:text-indigo-600';
  const active = 'text-indigo-600 border-b-2 border-indigo-600 pb-1';

  return (
    <header className="bg-white shadow">
      <nav className="container mx-auto px-6 py-4 flex items-center justify-between">
        <div className="text-2xl font-bold text-indigo-600">Trading Bot Maker</div>
        <div className="flex space-x-8">
          <NavLink to="/connect"    className={({isActive})=> isActive?active:base }>Connect Coinbase</NavLink>
          <NavLink to="/new"        className={({isActive})=> isActive?active:base }>New Bot</NavLink>
          <NavLink to="/bots"       className={({isActive})=> isActive?active:base }>Bots</NavLink>
          <NavLink to="/dashboard"  className={({isActive})=> isActive?active:base }>Dashboard</NavLink>
        </div>
      </nav>
    </header>
  );
}
