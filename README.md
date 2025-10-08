# GlobalXchange FinAid - Backend API

Python Flask API with LangChain-powered financial AI agents using Azure OpenAI.

## 🏗️ Architecture

- **Framework**: Flask with Blueprint architecture
- **AI Provider**: Azure OpenAI (GPT-4) with fallback support
- **Agent System**: LangChain-based financial AI agents
- **Data Processing**: Pandas for CSV/Excel handling
- **Deployment**: Render.com ready

## 🤖 AI Agents

### COA Generator
- Generates Chart of Accounts based on business requirements
- Supports multiple accounting standards (US GAAP, IFRS, etc.)
- Customizable account codes and categories

### Category Predictor
- Predicts transaction categories and payees
- Uses vector similarity for enhanced accuracy
- Supports bulk transaction processing

### Sheet Functions
- Generates P&L statements and Balance Sheets
- Calculates closing balances and financial ratios
- Financial impact analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Azure OpenAI resource with GPT-4 deployment

### Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Configure your Azure OpenAI credentials in .env
python app.py
```

Server runs on `http://localhost:3000`

## 🔧 Environment Variables

Required in `.env`:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_MODEL_NAME=gpt-4
```

## 📋 API Endpoints

### COA Generator
- `POST /api/coa-generator/generate-csv` - Generate COA from categories
- `POST /api/coa-generator/generate-desc` - Generate COA from description

### Category Predictor
- `POST /api/category-predictor/categorize-transactions/csv` - Categorize transactions

### Sheet Functions
- `POST /api/sheet-functions/generate-pl` - Generate P&L statement
- `POST /api/sheet-functions/generate-bs` - Generate Balance Sheet

## 🏛️ Project Structure

```
├── src/
│   ├── agents/              # AI agent implementations
│   │   ├── coa_generator/   # Chart of Accounts generator
│   │   ├── predictor_type_1/# Transaction categorizer v1
│   │   └── predictor_type_2/# Transaction categorizer v2
│   ├── server/              # Flask app configuration
│   │   ├── controllers/     # API route handlers
│   │   └── config/          # Environment configurations
│   └── utils/               # Utility functions
├── app.py                   # Application entry point
└── requirements.txt         # Dependencies
```

## 🔄 Development

### Adding New Agents
1. Create agent directory in `src/agents/`
2. Implement chains in `chains/` subdirectory
3. Add controller in `src/server/controllers/`
4. Register blueprint in `src/server/routes.py`

### Testing
```bash
python test.py  # Test agent chains
```

## 🚀 Deployment

### Render.com
1. Connect this repository to Render
2. Create Web Service with:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
3. Set environment variables in Render dashboard

### Local Development
```bash
./start.sh  # Unix/macOS
# OR
python app.py  # All platforms
```

## 👥 Maintained by

**vithaluntold** (vithal@financegroup.com)

## 📄 License

Private - All rights reserved