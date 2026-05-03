# AI File Generator 🚀

**Cloud-native AI file generator** - Generate professional documents (PDF, Excel, Word) from natural language prompts using cloud-based AI APIs.

## ✨ Features

- 🔀 **Multi-Backend Routing**: OpenRouter (100+ models) + HuggingFace fallback
- ☁️ **Cloud-Only**: No Ollama, no local installation needed
- 💨 **Ultra-Fast Setup**: Works on any laptop/device with just API keys
- 🎯 **Smart Caching**: Avoid repeated API calls (in-memory, 24h TTL)
- 🛡️ **Timeout Protected**: 30-second hard limits on all API calls
- 📊 **Professional Output**: PDF, Excel, Word, CSV, JSON formats
- 🔄 **Auto-Retry**: Enhanced parameters on first failure
- 📋 **Template Fallback**: Works without API keys
- 🚀 **Production-Ready**: Docker, systemd services, comprehensive logging

## 🚀 Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/nothingnullnuke-blip/ai-file-generator.git
cd ai-file-generator
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get Free API Keys

**OpenRouter** (recommended):
1. Go to https://openrouter.ai/keys
2. Sign up (free $5 credits)
3. Copy API key

**HuggingFace** (backup):
1. Go to https://huggingface.co/settings/tokens
2. Create token
3. Copy it

### 4. Configure Environment

```bash
# Copy example config
copy .env.example .env
# Mac/Linux: cp .env.example .env

# Edit .env and add your API keys
# Windows: notepad .env
# Mac/Linux: nano .env
```

Your `.env` should look like:
```
OR_API_KEY=sk-your-openrouter-key-here
OR_MODEL=mistralai/mistral-7b-instruct
HF_API_KEY=hf_your-huggingface-token-here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### 5. Test on Your Laptop

```bash
# Test CLI (generate PDF)
python cli/main.py generate -p "Create a sales report" -f pdf

# Run web API
python api/main.py

# Open browser: http://localhost:8000/docs
```

## 📖 Usage

### CLI

```bash
# Generate PDF from prompt
python cli/main.py generate -p "Create a quarterly sales report" -f pdf

# Generate Excel
python cli/main.py generate -p "Sales data by region" -f excel

# Generate Word document
python cli/main.py generate -p "Create an invoice" -f docx

# Other formats
python cli/main.py generate -p "Sales data" -f csv
python cli/main.py generate -p "Report data" -f json

# Show system info
python cli/main.py info
```

### API (Web)

**Start server:**
```bash
python api/main.py
# Visit http://localhost:8000/docs for interactive docs
```

**Generate file:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a sales report",
    "file_type": "pdf",
    "color_scheme": "professional"
  }'
```

**Check cache:**
```bash
curl http://localhost:8000/cache/stats
```

**List generated files:**
```bash
curl http://localhost:8000/files
```

**Download file:**
```bash
curl http://localhost:8000/files/report_20240503_120000.pdf -o report.pdf
```

### Python Code

```python
from ai_engine.prompt_processor import PromptProcessor
from generators.pdf_generator import PDFGenerator

processor = PromptProcessor()
output = processor.process(
    "Create a quarterly sales report with metrics",
    file_type="pdf"
)

generator = PDFGenerator(output)
filepath = generator.generate()
print(f"Generated: {filepath}")
```

## 🏗️ Project Structure

```
ai-file-generator/
├── ai_engine/                 # AI processing
│   ├── prompt_processor.py    # Main AI processor with caching
│   ├── json_validator.py      # JSON extraction & repair
│   ├── openrouter_backend.py  # OpenRouter (100+ models)
│   └── huggingface_backend.py # HuggingFace fallback
├── generators/                # File generation
│   ├── base_generator.py      # Abstract base class
│   ├── pdf_generator.py       # PDF generation
│   ├── excel_generator.py     # Excel generation
│   ├── docx_generator.py      # Word documents
│   └── csv_json_generator.py  # Data export
├── templates/                 # Fallback templates
│   └── report_template.py     # Business templates
├── models/                    # Data models
│   └── schemas.py             # Pydantic schemas
├── api/                       # FastAPI server
│   └── main.py                # API endpoints
├── cli/                       # Command-line interface
│   └── main.py                # CLI commands
├── config/                    # Configuration
│   └── settings.py            # Settings management
├── utils/                     # Utilities
│   ├── logger.py              # Logging setup
│   └── validators.py          # Input validation
├── tests/                     # Tests
├── docker/                    # Docker deployment
├── requirements.txt           # Python dependencies
├── .env.example              # Example configuration
└── README.md                 # This file
```

## 🎯 How It Works

### Processing Pipeline

```
User Prompt
    ↓
[Backend Selection]
    ├→ Vague/Short (<20 chars) → Use Template
    ├→ Valid → Check Cache
    └→ If not cached → Call API
    ↓
OpenRouter or HuggingFace
    ↓
Validate & Repair JSON
    ↓
Convert to StructuredOutput
    ↓
On Failure → Retry with enhanced params
    ↓
On Retry Failure → Use Fallback Template
    ↓
Cache Result
    ↓
Generate File (PDF/Excel/Word)
```

### Backend Routing

The system intelligently selects the best backend:

| Condition | Backend | Reason |
|-----------|---------|--------|
| Valid prompt | OpenRouter | 100+ models, fast, production-ready |
| OpenRouter unavailable | HuggingFace | Free tier fallback |
| HuggingFace unavailable | Template | No API required |
| Short/vague prompt | Template | Skip API overhead |

## 🔧 Configuration

Edit `.env` to customize:

```env
# Primary backend (100+ models)
OR_API_KEY=your-key-here
OR_MODEL=mistralai/mistral-7b-instruct

# Fallback backend
HF_API_KEY=your-token-here
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# AI parameters
AI_TEMPERATURE=0.7        # 0=deterministic, 1=creative
AI_MAX_TOKENS=2048       # Response length
AI_TIMEOUT=30            # Seconds

# API server
API_HOST=0.0.0.0
API_PORT=8000

# Caching
CACHE_TTL_HOURS=24       # Cache expiry
CACHE_MAX_SIZE=100       # Max cached prompts
```

## 📊 Model Selection

### Free & Fast (Recommended)
- **OpenRouter**: `mistralai/mistral-7b-instruct`
- **HuggingFace**: `mistralai/Mistral-7B-Instruct-v0.2`

### Better Quality (Paid)
- **OpenRouter**: `openai/gpt-3.5-turbo`, `openai/gpt-4`
- **OpenRouter**: `anthropic/claude-2`

### Open Source
- **OpenRouter**: `meta-llama/llama-2-70b-chat`
- **HuggingFace**: `HuggingFaceH4/zephyr-7b-beta`

## 💻 System Requirements

- **OS**: Windows, macOS, Linux
- **Python**: 3.9+
- **RAM**: 512 MB minimum
- **Storage**: 500 MB for dependencies
- **Internet**: Required for API calls
- **GPU**: Not required

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -f docker/Dockerfile -t aigen .

# Run container
docker run -p 8000:8000 \
  -e OR_API_KEY=$OR_API_KEY \
  -e HF_API_KEY=$HF_API_KEY \
  aigen
```

### Oracle Cloud VM

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full instructions.

Quick setup:
```bash
SSH into Ubuntu VM
sudo apt install -y python3.10 python3.10-venv python3-pip git
git clone https://github.com/nothingnullnuke-blip/ai-file-generator.git
cd ai-file-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python api/main.py
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_generators.py -v

# Coverage
pytest --cov=. tests/
```

## ⚡ Performance

| Operation | Time |
|-----------|------|
| Cache hit | <100ms |
| OpenRouter call | 2-5s |
| File generation | <1s |
| **Total (first)** | 3-7s |
| **Total (cached)** | <200ms |

## 🔐 API Key Management

**Never commit `.env` file!**

For production:
1. Use environment variables
2. Use secrets manager
3. Rotate keys regularly
4. Monitor API usage

## 📝 Example Prompts

### Sales Report
```
Create a quarterly sales report showing:
- Revenue: $500K (up 12% YoY)
- Regional breakdown: North 35%, South 28%, East 22%, West 15%
- Monthly trend: Jan $100K, Feb $120K, Mar $145K
Include charts and recommendations.
```

### Invoice
```
Generate invoice for Acme Corp:
- Invoice #: INV-2024-001
- Service A: 1 × $500
- Service B: 2 × $250
- Tax: 10%
- Payment terms: Net 30
```

### Dashboard
```
Create dashboard showing:
- Active users: 1,250
- New signups: 150
- Revenue: $45,000
- Conversion rate: 3.5%
- Customer satisfaction: 4.7/5
Include trend charts.
```

## 🆘 Troubleshooting

### API Key Not Working
```
❌ OR_API_KEY not configured
✓ Solution: Add key to .env file
```

### Rate Limit Exceeded
```
❌ OpenRouter rate limit exceeded
✓ Solution: Use HuggingFace or wait before retrying
```

### API Timeout
```
❌ Timeout exceeded (30s)
✓ Solution: Use simpler prompt or increase AI_TIMEOUT
```

### File Not Found
```
❌ No module named 'pydantic'
✓ Solution: pip install -r requirements.txt
```

## 📚 API Documentation

Full interactive API docs available at:
**http://localhost:8000/docs** (Swagger UI)
**http://localhost:8000/redoc** (ReDoc)

### Endpoints

- `POST /generate` - Generate file
- `POST /generate-and-download` - Generate & download
- `GET /files` - List files
- `GET /files/{filename}` - Download file
- `DELETE /files/{filename}` - Delete file
- `GET /cache/stats` - Cache statistics
- `DELETE /cache` - Clear cache
- `GET /routing/analyze` - Show backend selection
- `GET /backends` - List available backends
- `GET /health` - Health check
- `GET /status` - System status

## 🤝 Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - See LICENSE file

## 🙏 Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](../../issues)
- 💬 [Discussions](../../discussions)
- 📧 Email: nothingnullnuke@gmail.com

## 🎯 Roadmap

- [ ] WebUI dashboard
- [ ] Batch processing
- [ ] Advanced templating
- [ ] Database integration
- [ ] User authentication
- [ ] Rate limiting
- [ ] Usage analytics

---

**Version**: 3.0.0 (Cloud-Native)
**Status**: Production-Ready ✅
**Cloud Backends**: OpenRouter + HuggingFace
**Local AI Required**: ❌ NO
**Last Updated**: 2024