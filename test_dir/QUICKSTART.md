# Quick Start Guide - Noha Interview Dashboard

## 🚀 Get Started in 5 Minutes

### Option 1: Using Docker (Recommended)

1. **Prerequisites**

   - Docker and Docker Compose installed
   - Git installed

2. **Clone and Start**

   ```bash
   cd test_dir
   cp backend/.env.example backend/.env
   cp frontend/noha/.env.example frontend/noha/.env

   # Edit backend/.env and add your API keys (OpenAI, etc.)

   docker-compose up -d
   ```

3. **Access the Application**

   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

4. **Login**
   - Email: `admin@noha.com`
   - Password: `Admin@123`

### Option 2: Manual Setup

#### Backend Setup

```bash
cd test_dir/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and configure your database and API keys

# Setup database
createdb noha_db
psql -d noha_db -f ../database/schema.sql

# Start server
python main.py
```

#### Frontend Setup

```bash
cd test_dir/frontend/noha

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

## 📝 Environment Variables to Configure

### Required for Backend

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT tokens
- `OPENAI_API_KEY` - OpenAI API key for reports

### Optional for Backend

- `REDIS_URL` - Redis connection (default: local)
- `GCS_BUCKET_NAME` - Google Cloud Storage bucket
- `CALENDLY_API_TOKEN` - Calendly integration
- `SMTP_*` - Email configuration

## 🎯 Next Steps

1. **Create Organizations**
   - Use the super admin account to create organizations
2. **Add Users**
   - Register recruiters, interviewers, and admins
3. **Create Positions**
   - Add job positions to track
4. **Schedule Interviews**
   - Start scheduling and conducting interviews

## 🐛 Troubleshooting

### Backend won't start

- Check database is running: `psql -d noha_db -c "SELECT 1;"`
- Check Redis is running: `redis-cli ping`
- Review logs: `docker-compose logs backend`

### Frontend can't connect to backend

- Verify backend is running: http://localhost:8000/health
- Check CORS settings in backend/.env
- Check VITE_API_BASE_URL in frontend/.env

### Database Schema Issues

- Re-run schema: `psql -d noha_db -f database/schema.sql`
- Or reset: `dropdb noha_db && createdb noha_db && psql -d noha_db -f database/schema.sql`

## 📚 Documentation

- Full README: See `README.md`
- API Docs: http://localhost:8000/api/docs (when running)
- Design Doc: `docs/noha_design.md`
- Requirements: `docs/noha_requirements.md`

## 🤝 Need Help?

The application includes:

- Interactive API documentation at `/api/docs`
- Sample data in the database schema
- Default admin account for testing

Happy interviewing! 🎉
