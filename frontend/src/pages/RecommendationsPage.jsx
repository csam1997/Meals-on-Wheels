import React, { useState, useEffect } from 'react';
import { apiClient } from '../config/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RecommendationsPage() {
  const [userId, setUserId] = useState('user_0001');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const data = await apiClient.post('/recommendations/individual', {
        user_id: userId,
        num_recommendations: 15,
        scope: 'individual',
      });
      setRecommendations(data);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Personalized Food Recommendations</h1>
      
      <div className="mb-6">
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter user ID (e.g., user_0001)"
          className="px-4 py-2 border rounded-lg w-full md:w-1/3 mb-3"
        />
        <button
          onClick={fetchRecommendations}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
        >
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {recommendations && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Recommendations for {recommendations.user_name}</h2>
          <p className="text-gray-600 mb-4">Budget: ${recommendations.budget} | Scope: {recommendations.scope}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.recommendations.map((rec, idx) => (
              <div key={idx} className="border rounded-lg p-4 hover:shadow-lg transition">
                <h3 className="font-bold text-lg">{rec.name}</h3>
                <p className="text-sm text-gray-600">{rec.category}</p>
                <p className="text-lg font-semibold mt-2">${rec.price}</p>
                <p className="text-sm text-blue-600 mt-2">{rec.reason}</p>
                <p className="text-xs text-gray-500 mt-2">Score: {rec.score.toFixed(0)}</p>
              </div>
            ))}
          </div>
          
          <div className="mt-6 p-4 bg-gray-100 rounded-lg">
            <h3 className="font-bold mb-2">Summary</h3>
            <p>Total Items: {recommendations.summary.total_recommendations}</p>
            <p>Estimated Cost: ${recommendations.summary.estimated_cost}</p>
          </div>
        </div>
      )}
    </div>
  );
}
