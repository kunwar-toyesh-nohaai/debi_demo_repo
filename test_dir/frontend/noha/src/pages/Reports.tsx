import React from 'react';
import { FileText } from 'lucide-react';

const Reports: React.FC = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Reports</h1>
          <p className="text-gray-600 mt-1">View AI-generated interview reports</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-12 text-center">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">Reports Module</h3>
        <p className="text-gray-500">Access interview analysis reports here</p>
      </div>
    </div>
  );
};

export default Reports;
