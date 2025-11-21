import React from 'react';
import { Settings as SettingsIcon } from 'lucide-react';

const Settings: React.FC = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Settings</h1>
          <p className="text-gray-600 mt-1">Configure your preferences</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-md p-12 text-center">
        <SettingsIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">Settings Module</h3>
        <p className="text-gray-500">Manage your account and system settings here</p>
      </div>
    </div>
  );
};

export default Settings;
