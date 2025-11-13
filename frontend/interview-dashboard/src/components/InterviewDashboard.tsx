import React, { useCallback, useEffect, useMemo, useState } from "react";

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
  created_at: string;
};

type DashboardData = {
  candidates: Candidate[];
  interviewers: Interviewer[];
  interviews: Interview[];
};

type ScheduleFormState = {
  candidateId: string;
  interviewerId: string;
  scheduledTime: string;
  location: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const getDefaultScheduleTime = (): string => {
  const defaultDate = new Date(Date.now() + 60 * 60 * 1000);
  return defaultDate.toISOString().slice(0, 16);
};

const InterviewDashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData>({
    candidates: [],
    interviewers: [],
    interviews: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [scheduleError, setScheduleError] = useState<string | null>(null);
  const [isSubmittingSchedule, setIsSubmittingSchedule] = useState(false);
  const [scheduleForm, setScheduleForm] = useState<ScheduleFormState>({
    candidateId: "",
    interviewerId: "",
    scheduledTime: getDefaultScheduleTime(),
    location: "",
  });

  const fetchDashboardData = useCallback(async (): Promise<DashboardData> => {
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

    return { candidates, interviewers, interviews };
  }, []);

  const refreshDashboard = useCallback(async () => {
    const dashboard = await fetchDashboardData();
    setData(dashboard);
  }, [fetchDashboardData]);

  useEffect(() => {
    let isMounted = true;

    async function loadInitialData() {
      setLoading(true);
      setError(null);

      try {
        const dashboard = await fetchDashboardData();
        if (isMounted) setData(dashboard);
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

    loadInitialData();

    return () => {
      isMounted = false;
    };
  }, [fetchDashboardData]);

  const handleOpenScheduler = () => {
    if (data.candidates.length === 0 || data.interviewers.length === 0) {
      setScheduleError("You need at least one candidate and one interviewer before scheduling an interview.");
    } else {
      setScheduleError(null);
    }
    setScheduleForm((prev) => ({
      ...prev,
      scheduledTime: prev.scheduledTime || getDefaultScheduleTime(),
    }));
    setShowScheduleModal(true);
  };

  const handleScheduleFieldChange = (updates: Partial<ScheduleFormState>) => {
    setScheduleForm((prev) => ({
      ...prev,
      ...updates,
    }));
  };

  const handleScheduleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!scheduleForm.candidateId || !scheduleForm.interviewerId || !scheduleForm.scheduledTime) {
      setScheduleError("Please select a candidate, interviewer, and time.");
      return;
    }

    setIsSubmittingSchedule(true);
    setScheduleError(null);

    const scheduledDate = new Date(scheduleForm.scheduledTime);

    try {
      if (Number.isNaN(scheduledDate.getTime())) {
        throw new Error("Please provide a valid date and time.");
      }

      const response = await fetch(`${API_BASE_URL}/interviews`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidate_id: Number(scheduleForm.candidateId),
          interviewer_id: Number(scheduleForm.interviewerId),
          scheduled_time: scheduledDate.toISOString(),
          status: "scheduled",
          location: scheduleForm.location.trim() || null,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Failed to schedule interview.");
      }

      await refreshDashboard();

      setScheduleForm({
        candidateId: "",
        interviewerId: "",
        scheduledTime: getDefaultScheduleTime(),
        location: "",
      });
      setShowScheduleModal(false);
    } catch (submitError) {
      setScheduleError(submitError instanceof Error ? submitError.message : "Failed to schedule interview.");
    } finally {
      setIsSubmittingSchedule(false);
    }
  };

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
        <div className="dashboard__header-text">
          <h1>Interview Dashboard</h1>
          <p>Monitor candidates, interviewers, and upcoming interviews at a glance.</p>
        </div>
        <button className="dashboard__action-button" type="button" onClick={handleOpenScheduler} disabled={loading}>
          Schedule Interview
        </button>
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

      {showScheduleModal && (
        <ScheduleInterviewModal
          candidates={data.candidates}
          interviewers={data.interviewers}
          formState={scheduleForm}
          onChange={handleScheduleFieldChange}
          onClose={() => {
            setShowScheduleModal(false);
            setScheduleError(null);
          }}
          onSubmit={handleScheduleSubmit}
          isSubmitting={isSubmittingSchedule}
          error={scheduleError}
        />
      )}
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

const ScheduleInterviewModal: React.FC<{
  candidates: Candidate[];
  interviewers: Interviewer[];
  formState: ScheduleFormState;
  onChange: (updates: Partial<ScheduleFormState>) => void;
  onClose: () => void;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  isSubmitting: boolean;
  error: string | null;
}> = ({ candidates, interviewers, formState, onChange, onClose, onSubmit, isSubmitting, error }) => {
  const isDisabled = candidates.length === 0 || interviewers.length === 0;

  return (
    <div className="scheduler-modal__backdrop" role="dialog" aria-modal="true">
      <div className="scheduler-modal">
        <header className="scheduler-modal__header">
          <h2>Schedule Interview</h2>
          <button type="button" className="scheduler-modal__close" onClick={onClose} aria-label="Close schedule form">
            ×
          </button>
        </header>

        <p className="scheduler-modal__hint">
          Choose a candidate, interviewer, and time to add a new interview to the dashboard.
        </p>

        {isDisabled ? (
          <div className="scheduler-modal__empty">
            You need at least one candidate and one interviewer before scheduling an interview.
          </div>
        ) : (
          <form className="scheduler-modal__form" onSubmit={onSubmit}>
            <label>
              Candidate
              <select
                value={formState.candidateId}
                onChange={(event) => onChange({ candidateId: event.target.value })}
                required
                disabled={isSubmitting}
              >
                <option value="">Select candidate</option>
                {candidates.map((candidate) => (
                  <option key={candidate.id} value={candidate.id}>
                    {candidate.full_name} — {candidate.position_applied}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Interviewer
              <select
                value={formState.interviewerId}
                onChange={(event) => onChange({ interviewerId: event.target.value })}
                required
                disabled={isSubmitting}
              >
                <option value="">Select interviewer</option>
                {interviewers.map((interviewer) => (
                  <option key={interviewer.id} value={interviewer.id}>
                    {interviewer.full_name}
                    {interviewer.department ? ` — ${interviewer.department}` : ""}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Scheduled time
              <input
                type="datetime-local"
                value={formState.scheduledTime}
                onChange={(event) => onChange({ scheduledTime: event.target.value })}
                required
                disabled={isSubmitting}
              />
            </label>

            <label>
              Location (optional)
              <input
                type="text"
                value={formState.location}
                onChange={(event) => onChange({ location: event.target.value })}
                placeholder="Office 4B, Zoom, etc."
                disabled={isSubmitting}
              />
            </label>

            {error && <div className="scheduler-modal__error">{error}</div>}

            <div className="scheduler-modal__actions">
              <button type="button" onClick={onClose} className="scheduler-modal__secondary" disabled={isSubmitting}>
                Cancel
              </button>
              <button type="submit" className="scheduler-modal__primary" disabled={isSubmitting}>
                {isSubmitting ? "Scheduling…" : "Schedule interview"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default InterviewDashboard;

