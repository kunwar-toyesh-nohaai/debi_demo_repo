import React, { useEffect, useState } from 'react';
import apiClient from '../lib/api';
import { format } from 'date-fns';
import { Calendar, Plus, Download, FileText, TrendingUp, Award, ChevronLeft, ChevronRight, Eye, Edit, Trash2 } from 'lucide-react';

interface Interview {
  id: string;
  scheduled_time: string;
  status: string;
  position_id: string;
  candidate_id: string;
  candidate_name?: string;
  candidate_email?: string;
  position?: string;
  competency?: string;
  duration_minutes: number;
  reschedule_count: number;
  recording_url?: string;
  plagiarism_report_url?: string;
  report_url?: string;
}

const Interviews: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    avgScore: 0,
    successRate: 0,
  });

  useEffect(() => {
    fetchInterviews();
  }, [filter]);

  const fetchInterviews = async () => {
    try {
      const params = filter !== 'all' ? { status_filter: filter } : {};
      const response = await apiClient.get('/interviews', { params });
      const interviewData = response.data;
      setInterviews(interviewData);

      // Calculate stats
      const total = interviewData.length;
      const completed = interviewData.filter((i: Interview) => i.status === 'COMPLETED').length;
      const successRate = total > 0 ? ((completed / total) * 100).toFixed(0) : 0;

      setStats({
        total,
        completed,
        avgScore: 0.1, // Placeholder
        successRate: Number(successRate),
      });
    } catch (error) {
      console.error('Failed to fetch interviews:', error);
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
          <h1 className="text-3xl font-bold text-gray-800">Interviews</h1>
          <p className="text-gray-600 mt-1">Manage and track all interview sessions</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-5 py-2.5 rounded-lg flex items-center gap-2 shadow-sm transition-all">
            <Download className="w-5 h-5" />
            Export
          </button>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg flex items-center gap-2 shadow-lg hover:shadow-xl transition-all">
            <Plus className="w-5 h-5" />
            Schedule Interview
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Total Interviews</p>
            <Calendar className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.total}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Completed</p>
            <FileText className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.completed}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Average Score</p>
            <TrendingUp className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.avgScore}</p>
        </div>

        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-medium text-gray-600">Success Rate</p>
            <Award className="w-5 h-5 text-gray-400" />
          </div>
          <p className="text-3xl font-bold text-gray-800">{stats.successRate}%</p>
        </div>
      </div>

      {/* Interviews Table */}
      <div className="bg-white rounded-xl shadow-md border border-gray-100">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">Interviews ({stats.total})</h2>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Search interviews..."
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">All Status</option>
                <option value="SCHEDULED">Scheduled</option>
                <option value="ONGOING">Ongoing</option>
                <option value="COMPLETED">Completed</option>
                <option value="FAILED">Failed</option>
                <option value="NO_SHOW">No Show</option>
                <option value="CANCELLED">Cancelled</option>
              </select>
              <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <option>All Positions</option>
              </select>
            </div>
          </div>
        </div>

        {interviews.length === 0 ? (
          <div className="p-12 text-center">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No interviews found</h3>
            <p className="text-gray-500">
              {filter === 'all'
                ? 'Schedule your first interview to get started'
                : `No ${filter.toLowerCase()} interviews`}
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Candidate</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Position</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Date</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Recording</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Report</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Plagiarism Report</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Competency</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Status</th>
                    <th className="text-left text-xs font-semibold text-gray-600 px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {interviews.map((interview) => (
                    <tr key={interview.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <p className="text-sm font-medium text-gray-800">
                            {interview.candidate_name || 'Ram'}
                          </p>
                          <p className="text-xs text-gray-500">
                            {interview.candidate_email || 'ram@noha.ai'}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {interview.position || 'Software Engineer'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {interview.scheduled_time
                          ? format(new Date(interview.scheduled_time), 'MMM dd, yyyy')
                          : 'Nov 13, 2025'}
                      </td>
                      <td className="px-6 py-4">
                        {interview.recording_url ? (
                          <a
                            href={interview.recording_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-700 text-xs flex items-center gap-1"
                          >
                            <FileText className="w-4 h-4" />
                            View
                          </a>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {interview.report_url ? (
                          <a
                            href={interview.report_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-green-600 hover:text-green-700 text-xs flex items-center gap-1"
                          >
                            <FileText className="w-4 h-4" />
                            View
                          </a>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {interview.plagiarism_report_url ? (
                          <a
                            href={interview.plagiarism_report_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-red-600 hover:text-red-700 text-xs flex items-center gap-1"
                          >
                            <FileText className="w-4 h-4" />
                            View
                          </a>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {interview.competency || 'Data structures and algorithm'}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(interview.status)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          <button
                            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            className="p-1.5 hover:bg-gray-100 rounded transition-colors"
                            title="Edit Interview"
                          >
                            <Edit className="w-4 h-4 text-gray-600" />
                          </button>
                          <button
                            className="p-1.5 hover:bg-red-50 rounded transition-colors"
                            title="Delete Interview"
                          >
                            <Trash2 className="w-4 h-4 text-red-600" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="p-4 border-t border-gray-200 flex items-center justify-center gap-2">
              <button className="p-2 hover:bg-gray-100 rounded transition-colors">
                <ChevronLeft className="w-5 h-5 text-gray-600" />
              </button>
              <button className="px-3 py-1 bg-indigo-600 text-white rounded">1</button>
              <button className="px-3 py-1 hover:bg-gray-100 text-gray-600 rounded">2</button>
              <button className="px-3 py-1 hover:bg-gray-100 text-gray-600 rounded">...</button>
              <button className="px-3 py-1 hover:bg-gray-100 text-gray-600 rounded">420</button>
              <button className="p-2 hover:bg-gray-100 rounded transition-colors">
                <ChevronRight className="w-5 h-5 text-gray-600" />
              </button>
              <button className="ml-4 px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded">Next</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Interviews;
