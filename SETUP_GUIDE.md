# AI File Generator - Complete Setup Guide

## ✅ Repository Verification

Your complete AI File Generator project is now on GitHub!

**Repository**: https://github.com/nothingnullnuke-blip/ai-file-generator

### ✨ What's Included

#### Core Modules
- ✅ `ai_engine/` - AI processing with OpenRouter & HuggingFace backends
- ✅ `generators/` - PDF, Excel, Word, CSV, JSON file generation
- ✅ `api/` - FastAPI server with 13 endpoints
- ✅ `cli/` - Command-line interface
- ✅ `config/` - Configuration management
- ✅ `models/` - Pydantic data models
- ✅ `templates/` - Fallback document templates
- ✅ `utils/` - Logger, validators
- ✅ `tests/` - Unit tests

#### Configuration Files
- ✅ `requirements.txt` - 15 dependencies
- ✅ `.env.example` - Environment configuration template
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Complete documentation
- ✅ `docker/Dockerfile` - Docker deployment

#### Total Files: 35+ files across all modules

---

## 🚀 Quick Start on Your Laptop (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/nothingnullnuke-blip/ai-file-generator.git
cd ai-file-generator
```

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Pydantic (data validation)
- FastAPI (web server)
- ReportLab (PDF generation)
- OpenPyXL (Excel generation)
- Python-docx (Word documents)
- Requests (API calls)
- Click (CLI)
- Pytest (testing)
- Matplotlib (charts)
- And more...

### Step 4: Get FREE API Keys

#### OpenRouter (Primary - Recommended)
1. Go to: https://openrouter.ai/keys
2. Click "Sign in with GitHub"
3. You get **$5 FREE credits** to test
4. Copy your API key

#### HuggingFace (Backup)
1. Go to: https://huggingface.co/settings/tokens
2. Create new token
3. Copy it

### Step 5: Configure Environment

```bash
# Copy example config
copy .env.example .env
# Mac/Linux: cp .env.example .env

# Edit file and paste your API keys
# Windows: Open in Notepad
# Mac/Linux: nano .env
```

Your `.env` should look like:
```
OR_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OR_MODEL=mistralai/mistral-7b-instruct
HF_API_KEY=hf_xxxxxxxxxxxxx
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Step 6: Test It!

**Generate a PDF:**
```bash
python cli/main.py generate -p "Create a sales report with Q1 and Q2 data" -f pdf
```

Check the `outputs/` folder for your generated PDF! 🎉

**Run the Web API:**
```bash
python api/main.py
```

Then open in browser: http://localhost:8000/docs

You'll see an interactive Swagger UI to test all endpoints!

---

## 📊 Complete File Structure

```
ai-file-generator/
│
├── ai_engine/
│   ├── __init__.py
│   ├── prompt_processor.py       (⭐ Main AI processor with caching)
│   ├── json_validator.py         (JSON repair & validation)
│   ├── openrouter_backend.py     (OpenRouter API - 100+ models)
│   └── huggingface_backend.py    (HuggingFace API - Fallback)
│
├── generators/
│   ├── __init__.py
│   ├── base_generator.py         (Abstract base class)
│   ├── pdf_generator.py          (PDF with charts & tables)
│   ├── excel_generator.py        (Excel with formatting)
│   ├── docx_generator.py         (Word documents)
│   └── csv_json_generator.py     (Data export)
│
├── templates/
│   ├── __init__.py
│   └── report_template.py        (Fallback templates)
│
├── models/
│   ├── __init__.py
│   └── schemas.py                (Pydantic models)
│
├── api/
│   ├── __init__.py
│   └── main.py                   (FastAPI server - 13 endpoints)
│
├── cli/
│   ├── __init__.py
│   └── main.py                   (CLI commands)
│
├── config/
│   ├── __init__.py
│   └── settings.py               (Configuration management)
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                 (Logging setup)
│   └── validators.py             (Input validation)
│
├── tests/
│   ├── __init__.py
│   ├── test_generators.py        (Generator tests)
│   └── test_json_validator.py    (JSON validator tests)
│
├── docker/
│   └── Dockerfile                (Docker deployment)
│
├── .gitignore                    (Git ignore rules)
├── .env.example                  (Configuration template)
├── requirements.txt              (Python dependencies)
└── README.md                     (Full documentation)
```

---

## 🎯 How to Use

### CLI (Command Line)

**Generate PDF:**
```bash
python cli/main.py generate \
  -p "Create quarterly sales report for 2024" \
  -f pdf \
  -c professional
```

**Generate Excel:**
```bash
python cli/main.py generate -p "Sales data by region" -f excel
```

**Generate Word:**
```bash
python cli/main.py generate -p "Create invoice for client" -f docx
```

**Show Info:**
```bash
python cli/main.py info
```

### Web API

**Start Server:**
```bash
python api/main.py
```

Visit: http://localhost:8000/docs

**Generate File (curl):**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create sales report",
    "file_type": "pdf",
    "color_scheme": "professional"
  }'
```

**List Generated Files:**
```bash
curl http://localhost:8000/files
```

**Download File:**
```bash
curl http://localhost:8000/files/report_*.pdf -o report.pdf
```

**Check Cache:**
```bash
curl http://localhost:8000/cache/stats
```

### Python Code

```python
from ai_engine.prompt_processor import PromptProcessor
from generators.pdf_generator import PDFGenerator

# Process prompt
processor = PromptProcessor()
output = processor.process(
    "Create a quarterly sales report",
    file_type="pdf"
)

# Generate file
generator = PDFGenerator(output)
filepath = generator.generate()
print(f"✅ Generated: {filepath}")
```

---

## 🔄 Workflow

### What Happens When You Submit a Prompt:

```
1. You submit prompt
   ↓
2. System checks cache (fast!)
   ├─ If found → return immediately
   └─ If not found → continue
   ↓
3. Analyze prompt type
   ├─ If short/vague → use template
   └─ If valid → call AI
   ↓
4. Call OpenRouter (or HuggingFace)
   ├─ If success → validate JSON
   └─ If failed → retry
   ↓
5. Validate & repair JSON output
   ├─ If valid → proceed
   └─ If invalid → use template
   ↓
6. Cache result for future use
   ↓
7. Convert to StructuredOutput
   ↓
8. Generate file (PDF/Excel/Word)
   ↓
9. Save to outputs/ folder
   ↓
10. Return file path ✅
```

---

## 🌍 Deployment (Later)

### Docker

```bash
# Build
docker build -f docker/Dockerfile -t aigen .

# Run
docker run -p 8000:8000 \
  -e OR_API_KEY=$OR_API_KEY \
  -e HF_API_KEY=$HF_API_KEY \
  aigen
```

### Oracle Cloud VM

When ready:
```bash
# SSH into VM
ssh -i key.pem ubuntu@your.vm.ip

# Clone repo
git clone https://github.com/nothingnullnuke-blip/ai-file-generator.git
cd ai-file-generator

# Setup (same as laptop)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with keys

# Run
python api/main.py
```

---

## 📚 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|----------|
| POST | `/generate` | Generate file |
| POST | `/generate-and-download` | Generate & download |
| GET | `/files` | List generated files |
| GET | `/files/{filename}` | Download file |
| DELETE | `/files/{filename}` | Delete file |
| GET | `/cache/stats` | Cache statistics |
| DELETE | `/cache` | Clear cache |
| GET | `/routing/analyze` | Show backend selection |
| GET | `/backends` | List available backends |
| GET | `/health` | Health check |
| GET | `/status` | System status |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc UI |

---

## 🎯 Key Features Explained

### 1. Multi-Backend Routing
- **OpenRouter**: 100+ models (GPT-4, Claude, Mistral, Llama)
- **HuggingFace**: Free tier fallback
- **Template**: Works without any API

### 2. Intelligent Caching
- In-memory cache (100 entries max)
- 24-hour TTL (time-to-live)
- Saves API costs & speeds up generation

### 3. Auto-Retry with Enhanced Parameters
- First attempt: Normal temperature (0.7)
- Second attempt: Low temperature (0.2) + stricter JSON instructions
- Fallback: Use template if both fail

### 4. JSON Repair
- Automatically fixes invalid JSON from AI
- Removes markdown code fences
- Fixes trailing commas
- Adds missing quotes

### 5. Timeout Protection
- 30-second hard limit on all API calls
- Prevents hanging/infinite waits
- Thread-safe implementation

---

## 🔧 Configuration Options

Edit `.env` to customize:

```env
# Primary AI Backend
OR_API_KEY=your_openrouter_key
OR_MODEL=mistralai/mistral-7b-instruct

# Fallback Backend
HF_API_KEY=your_huggingface_token
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# AI Parameters
AI_TEMPERATURE=0.7          # 0=deterministic, 1=creative
AI_MAX_TOKENS=2048         # Response length
AI_TIMEOUT=30              # Seconds

# API Server
API_HOST=0.0.0.0           # Bind address
API_PORT=8000              # Port
API_WORKERS=4              # Worker threads

# Caching
CACHE_TTL_HOURS=24         # Cache expiry
CACHE_MAX_SIZE=100         # Max cached prompts

# File Generation
MAX_FILE_SIZE_MB=100       # Max output size
MAX_PROMPT_LENGTH=5000     # Max input length
MIN_PROMPT_LENGTH=10       # Min input length
```

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pydantic'`
**Fix:**
```bash
pip install -r requirements.txt
```

### Issue: `OR_API_KEY not configured`
**Fix:**
1. Open `.env` file
2. Add your OpenRouter API key
3. Save file
4. Restart application

### Issue: Port 8000 already in use
**Fix:**
```bash
# Change port in .env
API_PORT=8001

# Or kill process on port 8000
# Windows: netstat -ano | findstr :8000
# Linux: lsof -i :8000 && kill -9 <PID>
```

### Issue: API timeout
**Fix:**
1. Use simpler, shorter prompts
2. Increase timeout: `AI_TIMEOUT=60`
3. Check internet connection
4. Try HuggingFace if OpenRouter is slow

---

## 📈 Next Steps

### After Testing on Laptop:
1. ✅ Verify all features work
2. ✅ Generate a few test documents
3. ✅ Try different prompts
4. ✅ Test both CLI and API

### Before Deploying to Cloud:
1. Push any changes to GitHub
2. Set up Oracle Cloud VM
3. Clone repository on VM
4. Configure API keys
5. Run on cloud server
6. Test from public IP

---

## 📞 Support

If you run into issues:

1. **Check logs**: `tail -f logs/main.log`
2. **Read README**: Full documentation in `README.md`
3. **Check API docs**: http://localhost:8000/docs
4. **Test command**: `python cli/main.py info`

---

## 🎉 Success Checklist

- ✅ Repository cloned
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ API keys added to `.env`
- ✅ CLI test successful
- ✅ API server running
- ✅ First document generated

**You're ready to go! 🚀**

---

**Questions?** Email: nothingnullnuke@gmail.com
**Repository**: https://github.com/nothingnullnuke-blip/ai-file-generator
