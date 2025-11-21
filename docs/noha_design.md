# Noha Interview Service Dashboard - Design Document

**Version:** 1.0  
**Date:** November 20, 2025  
**Project:** Noha

---

## 1. Introduction

### 1.1. Purpose

This Design Document (SDD) describes the architecture, system design, and technical implementation details for the Noha Interview Service Dashboard. It translates the requirements defined in the SRS into a technical blueprint for development.

### 1.2. Scope

The design covers the full stack implementation including:

- Frontend Web Application
- Backend API Services
- Database Schema
- External Integrations (Calendly, OpenAI, GCS)
- Infrastructure & Security

---

## 2. System Architecture

### 2.1. High-Level Architecture

Noha follows a **Modular Monolith** architecture to balance development speed with scalability. The system is composed of a Single Page Application (SPA) frontend communicating with a RESTful backend API.

**Key Components:**

1.  **Client Layer**: React-based SPA running in the browser.
2.  **API Gateway / Load Balancer**: Nginx reverse proxy handling SSL termination and request routing.
3.  **Application Server**: FastAPI (Python) backend handling business logic.
4.  **Data Layer**: PostgreSQL for relational data, Redis for caching and session management.
5.  **Storage Layer**: Google Cloud Storage (GCS) for large binary files (videos, recordings).
6.  **External Services**:
    - **Calendly**: For scheduling and availability.
    - **OpenAI**: For interview analysis and report generation.
    - **SMTP Server**: For email notifications.

### 2.2. Communication Patterns

- **Client-Server**: REST API (JSON) over HTTPS.
- **Real-Time**: WebSockets for signaling (WebRTC setup) and live status updates.
- **Video/Audio**: WebRTC (Peer-to-Peer) with TURN/STUN servers for NAT traversal.
- **Async Tasks**: Background workers (Celery) for video processing and report generation.

---

## 3. Technology Stack

### 3.1. Frontend

- **Framework**: React 18+ (Vite)
- **Language**: TypeScript
- **Styling**: TailwindCSS (v3.4+)
- **State Management**: Zustand or React Query
- **Video/WebRTC**: `simple-peer` or native WebRTC API
- **Routing**: React Router v6

### 3.2. Backend

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy (Async)
- **Migrations**: Alembic
- **Task Queue**: Celery with Redis
- **Validation**: Pydantic

### 3.3. Database & Storage

- **Primary DB**: PostgreSQL 15+
- **Cache/Broker**: Redis 7+
- **Object Storage**: Google Cloud Storage (GCS)

### 3.4. Infrastructure

- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions

---

## 4. Database Design

### 4.1. Entity Relationship Diagram (Description)

The database schema centers around the `Organization` tenant.

#### **Tables:**

1.  **organizations**

    - `id` (UUID, PK)
    - `name` (String)
    - `domain` (String)
    - `created_at` (Timestamp)

2.  **users**

    - `id` (UUID, PK)
    - `org_id` (UUID, FK -> organizations.id)
    - `email` (String, Unique)
    - `password_hash` (String)
    - `role` (Enum: SUPER_ADMIN, ADMIN, HIRING_MANAGER, RECRUITER, INTERVIEWER)
    - `full_name` (String)
    - `calendly_link` (String, Nullable)

3.  **positions**

    - `id` (UUID, PK)
    - `org_id` (UUID, FK)
    - `title` (String)
    - `status` (Enum: OPEN, CLOSED)
    - `closed_at` (Timestamp, Nullable)

4.  **candidates**

    - `id` (UUID, PK)
    - `org_id` (UUID, FK)
    - `email` (String)
    - `full_name` (String)
    - `phone` (String)
    - `resume_url` (String)

5.  **interviews**

    - `id` (UUID, PK)
    - `org_id` (UUID, FK)
    - `position_id` (UUID, FK)
    - `candidate_id` (UUID, FK)
    - `scheduled_time` (Timestamp)
    - `status` (Enum: SCHEDULED, ONGOING, COMPLETED, FAILED, NO_SHOW, CANCELLED)
    - `calendly_event_id` (String)
    - `reschedule_count` (Int, Default 0)
    - `meeting_link` (String)
    - `recording_url` (String, Nullable)
    - `transcript_url` (String, Nullable)

6.  **interview_participants** (Join Table)

    - `interview_id` (UUID, FK)
    - `user_id` (UUID, FK)

7.  **reports**
    - `id` (UUID, PK)
    - `interview_id` (UUID, FK -> interviews.id)
    - `summary` (Text)
    - `strengths` (JSONB)
    - `weaknesses` (JSONB)
    - `rating` (Int)
    - `generated_at` (Timestamp)

---

## 5. API Design

### 5.1. Authentication

- `POST /api/v1/auth/login` -> { access_token, refresh_token }
- `POST /api/v1/auth/register` -> { user_id } (Admin only)
- `POST /api/v1/auth/refresh`

### 5.2. Interviews

- `GET /api/v1/interviews` (Filter by status, date, candidate)
- `POST /api/v1/interviews` (Create/Schedule)
- `GET /api/v1/interviews/{id}`
- `PATCH /api/v1/interviews/{id}/reschedule`
- `POST /api/v1/interviews/{id}/cancel`
- `POST /api/v1/interviews/{id}/start` (Triggers recording)
- `POST /api/v1/interviews/{id}/end` (Triggers processing)

### 5.3. Reports

- `GET /api/v1/reports/{interview_id}`
- `POST /api/v1/reports/{interview_id}/regenerate`

### 5.4. WebSockets

- `/ws/interview/{interview_id}`
  - Events: `offer`, `answer`, `ice-candidate`, `chat-message`, `status-change`

---

## 6. Component Design (Frontend)

### 6.1. Core Layout

- **Sidebar**: Navigation (Dashboard, Interviews, Candidates, Settings).
- **Header**: User profile, Organization switcher (if Super Admin), Notifications.
- **Main Content**: Dynamic route outlet.

### 6.2. Key Modules

#### **Dashboard Module**

- **StatsCards**: Total interviews, Pending reports, etc.
- **UpcomingList**: List of interviews scheduled for today/tomorrow.

#### **Interview Room Module**

- **VideoContainer**: Handles WebRTC streams (Local + Remote).
- **Controls**: Mute, Camera Off, Screen Share, End Call.
- **ChatBox**: Real-time text chat.
- **Timer**: 45-minute countdown.

#### **Scheduling Module**

- **CalendlyWidget**: Embedded Calendly iframe or API integration for slot selection.
- **CandidateForm**: Input for candidate details.

#### **Report Module**

- **ReportView**: Displays AI analysis.
- **PDFExport**: Button to download report.

---

## 7. External Integrations

### 7.1. OpenAI Integration

- **Model**: GPT-4o (or latest stable).
- **Input**: Full transcript of the interview.
- **System Prompt**: "You are an expert HR analyst. Analyze the following interview transcript. Extract key strengths, weaknesses, and provide a fit assessment score (1-10). Format output as JSON."
- **Processing**: Asynchronous background task triggered after interview completion.

### 7.2. Calendly Integration

- **Webhooks**: Listen for `invitee.created` and `invitee.canceled` events to sync status.
- **API**: Use Calendly API to fetch recruiter availability slots if custom UI is built, or embed Calendly scheduling page.

### 7.3. Google Cloud Storage (GCS)

- **Uploads**: Use Signed URLs for direct browser-to-GCS uploads of recordings to reduce server load.
- **Access**: Generate short-lived signed URLs for viewing recordings securely.

---

## 8. Security Design

1.  **Data Encryption**:
    - TLS 1.3 for all data in transit.
    - AES-256 for database volume encryption.
2.  **Access Control**:
    - Middleware to check JWT scopes against route requirements.
    - Row-Level Security (RLS) logic in application layer (always filter by `org_id`).
3.  **Video Security**:
    - Ephemeral WebRTC tokens.
    - Recordings stored in private GCS buckets, accessible only via signed URLs.

---

## 9. UI/UX Design Guidelines

### 9.1. Color Palette

- **Primary**: Deep Indigo (`#4F46E5`) - Trust, Professionalism.
- **Secondary**: Teal (`#14B8A6`) - Growth, Success.
- **Background**: Slate (`#F8FAFC`) - Clean, Modern.
- **Surface**: White (`#FFFFFF`) - Cards, Modals.
- **Error**: Rose (`#E11D48`).

### 9.2. Typography

- **Font Family**: 'Inter' or 'Roboto'.
- **Headings**: Bold, High Contrast.
- **Body**: Regular, legible size (16px).

### 9.3. Interaction

- **Hover Effects**: Subtle lift (shadow increase) on cards.
- **Transitions**: Smooth ease-in-out (200ms) for all state changes.
- **Feedback**: Toast notifications for success/error states.

---
