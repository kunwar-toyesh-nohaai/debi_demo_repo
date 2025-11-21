import React, { useEffect, useState } from 'react';
import apiClient from '../lib/api';
import { Calendar, Users, TrendingUp, Clock, Plus, BarChart3, Star, UserCircle } from 'lucide-react';
import { format } from 'date-fns';
import { useAuthStore } from '../store/authStore';

interface DashboardStats {
  total_interviews: number;
  scheduled_interviews: number;
  completed_interviews: number;
  pending_reports: number;
  total_candidates: number;
  total_positions: number;
}

interface RecentInterview {
  id: string;
  candidate_name: string;
  position: string;
  scheduled_time: string;
  status: string;
  score?: number;
  duration_minutes?: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentInterviews, setRecentInterviews] = useState<RecentInterview[]>([]);
  const [loading, setLoading] = useState(true);
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, interviewsResponse] = await Promise.all([
        apiClient.get('/interviews/dashboard/stats'),
        apiClient.get('/interviews?limit=5'),
      ]);
      
      setStats(statsResponse.data);
      setRecentInterviews(interviewsResponse.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      SCHEDULED: 'bg-yellow-100 text-yellow-800',
      ONGOING: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      FAILED: 'bg-red-100 text-red-800',
      NO_SHOW: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  const calculateSuccessRate = () => {
    if (!stats || stats.total_interviews === 0) return '0.0';
    const rate = (stats.completed_interviews / stats.total_interviews) * 100;
    return rate.toFixed(1);
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
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-700 rounded-2xl shadow-xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.full_name || 'User'}!</h1>
            <p className="text-indigo-100 text-lg mb-6">
              Monitor your AI-powered interviews, track candidate performance, and manage your hiring pipeline with ease.
            </p>
            <div className="flex gap-4">
              <button className="bg-white text-indigo-600 px-6 py-3 rounded-lg font-semibold hover:bg-indigo-50 transition-all shadow-lg flex items-center gap-2">
                <Plus className="w-5 h-5" />
                Schedule Interview
              </button>
              <button className="bg-indigo-500 bg-opacity-30 backdrop-blur-sm text-white px-6 py-3 rounded-lg font-semibold hover:bg-opacity-40 transition-all border border-white border-opacity-20 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                View Analytics
              </button>
            </div>
          </div>
          <div className="hidden lg:block">
            <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-full p-8 border border-white border-opacity-20">
              <UserCircle className="w-24 h-24 text-white" />
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total Interviews</p>
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats?.total_interviews || 0}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Active Candidates</p>
            <Users className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats?.total_candidates || 0}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Success Rate</p>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{calculateSuccessRate()}%</p>
        </div>

        <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Avg Duration</p>
            <Clock className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">0 min</p>
        </div>
      </div>

      {/* Recent Interviews and Top Performers */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Interviews */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">Recent Interviews</h2>
            <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1">
              View All
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          {recentInterviews.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500">No recent interviews to display</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Candidate</th>
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Position</th>
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Date</th>
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Status</th>
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Score</th>
                    <th className="text-left text-xs font-semibold text-gray-600 pb-3">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {recentInterviews.map((interview) => (
                    <tr key={interview.id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 text-sm font-medium text-gray-800">
                        {interview.candidate_name || 'Ram'}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {interview.position || 'Software Engineer'}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {interview.scheduled_time 
                          ? format(new Date(interview.scheduled_time), 'MMM dd, yyyy')
                          : 'Nov 13, 2025'}
                      </td>
                      <td className="py-3">
                        {getStatusBadge(interview.status)}
                      </td>
                      <td className="py-3">
                        {interview.score ? (
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${
                            interview.score >= 7 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {interview.score.toFixed(1)}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {interview.duration_minutes ? `${interview.duration_minutes} min` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Top Performers */}
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center gap-2 mb-6">
            <Star className="w-5 h-5 text-yellow-500" />
            <h2 className="text-xl font-bold text-gray-800">Top Performers</h2>
          </div>
          
          <div className="text-center py-8">
            <div className="bg-gray-100 rounded-full p-6 w-20 h-20 mx-auto mb-3 flex items-center justify-center">
              <Star className="w-10 h-10 text-gray-400" />
            </div>
            <p className="text-gray-500 text-sm">No completed interviews yet</p>
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-500 text-center mt-8">
        Latest interview sessions and their status
      </div>
    </div>
  );
};

export default Dashboard;
