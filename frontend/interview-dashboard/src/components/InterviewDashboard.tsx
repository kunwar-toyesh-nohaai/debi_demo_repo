import React, { useEffect, useMemo, useState } from "react";

type Candidate = {
  id: number;
  full_name: string;
  email: string;
  position_applied: string;
  phone?: string | null;
};

type Interviewer = {
  id: number;
  full_name: string;
  email: string;
  department?: string | null;
};

type Interview = {
  id: number;
  candidate_id: number;
  interviewer_id: number;
  scheduled_time: string;
  status: string;
  location?: string | null;
};

type DashboardData = {
  candidates: Candidate[];
  interviewers: Interviewer[];
  interviews: Interview[];
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const InterviewDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData>({
    candidates: [],
    interviewers: [],
    interviews: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const [candidatesRes, interviewersRes, interviewsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/candidates`),
          fetch(`${API_BASE_URL}/interviewers`),
          fetch(`${API_BASE_URL}/interviews`),
        ]);

        if (!candidatesRes.ok || !interviewersRes.ok || !interviewsRes.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        const candidates = (await candidatesRes.json()) as Candidate[];
        const interviewers = (await interviewersRes.json()) as Interviewer[];
        const interviews = (await interviewsRes.json()) as Interview[];

        if (isMounted) {
          setData({ candidates, interviewers, interviews });
        }
      } catch (fetchError) {
        if (isMounted) {
          setError(fetchError instanceof Error ? fetchError.message : "Unknown error");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  const stats = useMemo(() => {
    const upcomingInterviews = data.interviews.filter((interview) => {
      const interviewDate = new Date(interview.scheduled_time);
      const now = new Date();
      return interviewDate >= now;
    });

    const scheduledCount = upcomingInterviews.length;
    const completedCount = data.interviews.filter((interview) => interview.status === "completed").length;
    const pendingFeedbackCount = data.interviews.filter((interview) => interview.status === "awaiting_feedback").length;

    return {
      candidateCount: data.candidates.length,
      interviewerCount: data.interviewers.length,
      scheduledCount,
      completedCount,
      pendingFeedbackCount,
    };
  }, [data]);

  if (loading) {
    return <div className="dashboard dashboard--loading">Loading dashboard…</div>;
  }

  if (error) {
    return (
      <div className="dashboard dashboard--error">
        <h2>Something went wrong</h2>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>Interview Dashboard</h1>
        <p>Monitor candidates, interviewers, and upcoming interviews at a glance.</p>
      </header>

      <section className="dashboard__stats">
        <StatCard label="Candidates" value={stats.candidateCount} />
        <StatCard label="Interviewers" value={stats.interviewerCount} />
        <StatCard label="Upcoming Interviews" value={stats.scheduledCount} />
        <StatCard label="Completed" value={stats.completedCount} />
        <StatCard label="Awaiting Feedback" value={stats.pendingFeedbackCount} />
      </section>

      <section className="dashboard__content">
        <div className="dashboard__panel">
          <h2>Upcoming Interviews</h2>
          <InterviewTable interviews={data.interviews} candidates={data.candidates} interviewers={data.interviewers} />
        </div>

        <div className="dashboard__panel">
          <h2>Recent Candidates</h2>
          <CandidateList candidates={data.candidates.slice(0, 5)} />
        </div>
      </section>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="stat-card">
    <div className="stat-card__label">{label}</div>
    <div className="stat-card__value">{value}</div>
  </div>
);

const InterviewTable: React.FC<{
  interviews: Interview[];
  candidates: Candidate[];
  interviewers: Interviewer[];
}> = ({ interviews, candidates, interviewers }) => {
  const candidateLookup = useMemo(
    () => Object.fromEntries(candidates.map((candidate) => [candidate.id, candidate.full_name])),
    [candidates]
  );
  const interviewerLookup = useMemo(
    () => Object.fromEntries(interviewers.map((interviewer) => [interviewer.id, interviewer.full_name])),
    [interviewers]
  );

  const sortedInterviews = useMemo(() => {
    return [...interviews].sort((a, b) => {
      return new Date(b.scheduled_time).getTime() - new Date(a.scheduled_time).getTime();
    });
  }, [interviews]);

  if (sortedInterviews.length === 0) {
    return <p>No interviews scheduled yet.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Interviewer</th>
          <th>Scheduled</th>
          <th>Status</th>
          <th>Location</th>
        </tr>
      </thead>
      <tbody>
        {sortedInterviews.slice(0, 8).map((interview) => (
          <tr key={interview.id}>
            <td>{candidateLookup[interview.candidate_id] ?? "Unknown"}</td>
            <td>{interviewerLookup[interview.interviewer_id] ?? "Unknown"}</td>
            <td>{new Date(interview.scheduled_time).toLocaleString()}</td>
            <td>{interview.status}</td>
            <td>{interview.location ?? "N/A"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

const CandidateList: React.FC<{ candidates: Candidate[] }> = ({ candidates }) => {
  if (candidates.length === 0) {
    return <p>No candidates recorded yet.</p>;
  }

  return (
    <ul className="candidate-list">
      {candidates.map((candidate) => (
        <li key={candidate.id} className="candidate-list__item">
          <strong>{candidate.full_name}</strong>
          <div>{candidate.email}</div>
          <div>{candidate.position_applied}</div>
        </li>
      ))}
    </ul>
  );
};

export default InterviewDashboard;

