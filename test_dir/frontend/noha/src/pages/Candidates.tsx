import React from 'react';
import { Users } from 'lucide-react';

const Candidates: React.FC = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Candidates</h1>
          <p className="text-gray-600 mt-1">Manage candidate information</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-12 text-center">
        <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">Candidates Module</h3>
        <p className="text-gray-500">View and manage all candidates here</p>
      </div>
    </div>
  );
};

export default Candidates;
