import React, { useEffect, useState } from 'react';
import { Briefcase, Plus, MoreVertical, Copy } from 'lucide-react';
import apiClient from '../lib/api';

interface JobRole {
  id: string;
  name: string;
  level: string;
  competencies: string[];
  created_at: string;
}

const Positions: React.FC = () => {
  const [jobRoles, setJobRoles] = useState<JobRole[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    junior: 0,
    senior: 0,
  });

  useEffect(() => {
    fetchJobRoles();
  }, []);

  const fetchJobRoles = async () => {
    try {
      const response = await apiClient.get('/job-roles');
      const roles = response.data;
      setJobRoles(roles);
      
      // Calculate stats
      const total = roles.length;
      const junior = roles.filter((r: JobRole) => r.level === 'L1' || r.level === 'Junior').length;
      const senior = roles.filter((r: JobRole) => r.level === 'Senior' || r.level === 'L3').length;
      
      setStats({ total, junior, senior });
    } catch (error) {
      console.error('Failed to fetch job roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelBadge = (level: string) => {
    const styles: Record<string, string> = {
      L1: 'bg-teal-100 text-teal-800',
      L2: 'bg-teal-100 text-teal-800',
      L3: 'bg-teal-100 text-teal-800',
      Junior: 'bg-teal-100 text-teal-800',
      Senior: 'bg-teal-100 text-teal-800',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[level] || 'bg-gray-100 text-gray-800'}`}>
        {level}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Job Roles</h1>
          <p className="text-gray-600 mt-1">
            Create and manage job roles with their competencies and interview configurations.
          </p>
        </div>
        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 shadow-lg hover:shadow-xl transition-all">
          <Plus className="w-5 h-5" />
          Create Job Role
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6 border-2 border-indigo-200">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total Job Roles</p>
            <Copy className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-4xl font-bold text-gray-800">{stats.total}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Junior Roles</p>
            <Copy className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-4xl font-bold text-gray-800">{stats.junior}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Senior Roles</p>
            <Plus className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-4xl font-bold text-gray-800">{stats.senior}</p>
        </div>
      </div>

      {/* Job Roles Table */}
      <div className="bg-white rounded-xl shadow-md border border-gray-100">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-800">Job Roles</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage your job roles, their competencies, and interview configurations.
          </p>
        </div>

        {jobRoles.length === 0 ? (
          <div className="p-12 text-center">
            <Briefcase className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No job roles found</h3>
            <p className="text-gray-500">Create your first job role to get started</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Name</th>
                  <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Role Level</th>
                  <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Competencies</th>
                  <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {jobRoles.map((role) => (
                  <tr key={role.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-gray-800">
                      {role.name}
                    </td>
                    <td className="px-6 py-4">
                      {getLevelBadge(role.level)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-2">
                        {role.competencies && role.competencies.length > 0 ? (
                          role.competencies.slice(0, 5).map((comp, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                            >
                              {comp}
                            </span>
                          ))
                        ) : (
                          <span className="text-gray-400 text-xs">No competencies</span>
                        )}
                        {role.competencies && role.competencies.length > 5 && (
                          <span className="text-xs text-gray-500">
                            +{role.competencies.length - 5} more
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                        <MoreVertical className="w-5 h-5 text-gray-600" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Positions;
