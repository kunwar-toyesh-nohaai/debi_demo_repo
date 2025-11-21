# Noha Interview Service Dashboard

A comprehensive interview management platform for scheduling, conducting, and analyzing video interviews with AI-powered reporting.

## 🚀 Features

- **User Management**: Role-based access control (Super Admin, Admin, Hiring Manager, Recruiter, Interviewer)
- **Interview Scheduling**: Manual scheduling with Calendly integration
- **Video Interviews**: In-platform WebRTC video calls with recording
- **Candidate Tracking**: Monitor candidates through interview lifecycle
- **AI-Powered Reports**: Generate interview analysis using OpenAI
- **Multi-Organization**: Support for multiple organizations with data isolation
- **Email Notifications**: Automated notifications for scheduling, reminders, and updates

## 📁 Project Structure

```
test_dir/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/     # API endpoints
│   │   │   └── deps.py     # Dependencies
│   │   ├── core/           # Core configurations
│   │   ├── models/         # SQLAlchemy models
│   │   └── schemas/        # Pydantic schemas
│   ├── main.py             # Application entry point
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   └── noha/               # React Frontend
│       ├── src/
│       │   ├── components/ # Reusable components
│       │   ├── pages/      # Page components
│       │   ├── store/      # Zustand state management
│       │   └── lib/        # Utilities
│       ├── package.json
│       └── .env.example
└── database/
    └── schema.sql          # PostgreSQL schema
```

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy (Async)
- **Cache/Queue**: Redis
- **Storage**: Google Cloud Storage
- **AI**: OpenAI API
- **Calendar**: Calendly API

### Frontend

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State**: Zustand
- **Routing**: React Router
- **HTTP Client**: Axios
- **Video**: WebRTC (simple-peer)

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Google Cloud account (for GCS)
- OpenAI API key
- Calendly API token (optional)

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd test_dir/backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Setup PostgreSQL database**

   ```bash
   # Create database
   createdb noha_db

   # Run schema
   psql -d noha_db -f ../database/schema.sql
   ```

6. **Run the server**
   ```bash
   python main.py
   # Or with uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd test_dir/frontend/noha
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Default: VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Run development server**

   ```bash
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

## 🔐 Default Credentials

After running the schema, you can login with:

- **Email**: admin@noha.com
- **Password**: Admin@123

## 📋 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/noha_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
REFRESH_TOKEN_EXPIRE_DAYS=7

# Google Cloud Storage
GCS_BUCKET_NAME=noha-interview-storage
GOOGLE_APPLICATION_CREDENTIALS=./gcs-credentials.json

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Calendly
CALENDLY_API_TOKEN=your-calendly-token

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@noha.com

# CORS
ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 🎯 API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/register` - Register user (Admin only)
- `POST /api/v1/auth/logout` - Logout

### Interviews

- `GET /api/v1/interviews` - List interviews
- `POST /api/v1/interviews` - Create interview
- `GET /api/v1/interviews/{id}` - Get interview
- `PATCH /api/v1/interviews/{id}/reschedule` - Reschedule
- `POST /api/v1/interviews/{id}/cancel` - Cancel
- `POST /api/v1/interviews/{id}/start` - Start interview
- `POST /api/v1/interviews/{id}/end` - End interview

### Reports

- `GET /api/v1/reports/{interview_id}` - Get report
- `POST /api/v1/reports/{interview_id}/regenerate` - Regenerate report

### Dashboard

- `GET /api/v1/interviews/dashboard/stats` - Get statistics

## 📊 Database Schema

The database includes the following main tables:

- `organizations` - Multi-tenant organizations
- `users` - User accounts with roles
- `positions` - Job positions
- `candidates` - Candidate information
- `interviews` - Interview scheduling
- `interview_participants` - Interview attendees
- `reports` - AI-generated reports
- `email_notifications` - Notification logs
- `sessions` - JWT session management
- `audit_logs` - System audit trail

## 🎨 UI Features

- **Dashboard**: Statistics and overview
- **Interviews**: List, filter, and manage interviews
- **Candidates**: Manage candidate database
- **Positions**: Job position management
- **Reports**: View AI-generated interview insights
- **Settings**: User preferences and configuration

## 🔒 Security Features

- JWT-based authentication with refresh tokens
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Account lockout after failed attempts
- Secure session management
- CORS configuration
- Data encryption at rest and in transit

## 🚧 TODO / Future Enhancements

- [ ] WebRTC video call implementation
- [ ] Screen recording functionality
- [ ] Real-time transcription
- [ ] OpenAI report generation integration
- [ ] Calendly webhook integration
- [ ] Email notification sending
- [ ] File upload to GCS
- [ ] Advanced search and filtering
- [ ] Export reports to PDF
- [ ] Analytics dashboard
- [ ] Mobile responsive improvements

## 📝 License

This project is proprietary software developed for Noha.

## 👥 Support

For support and questions, contact the development team.

---

**Version**: 1.0.0  
**Last Updated**: November 20, 2025
