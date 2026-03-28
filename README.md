# 🔬 MF Portfolio X-Ray AI

> **AI-powered Mutual Fund Portfolio Analyzer** — Upload your CAMS/Kfintech CAS statement and get institutional-grade insights in seconds.

---

## 🏆 Built For
**Unstop Hackathon** — AI/Fintech Track

---

## 📌 Problem Statement

Indian retail investors hold mutual fund portfolios across multiple AMCs and fund types, but lack tools to:
- Understand their **true returns** vs benchmarks like Nifty 50
- Detect **fund overlap** and AMC concentration risk
- Get **actionable rebalancing advice** without paying a financial advisor

**MF Portfolio X-Ray AI** solves this by parsing official CAS PDFs and running AI-powered analysis using Groq's LLaMA 3.3 model.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **CAS PDF Parsing** | Parses official CAMS/Kfintech Consolidated Account Statements |
| 💰 **Investment Summary** | Total invested, current value, absolute gain/loss |
| 📊 **Absolute Return %** | Calculates portfolio return with formula breakdown |
| 🏆 **Best & Worst Fund** | Ranks all funds by performance |
| 🏦 **Nifty 50 Comparison** | Benchmarks your portfolio against Nifty 50's 14% avg |
| 🤖 **AI Verdict** | Groq LLaMA 3.3 generates a one-line portfolio verdict |
| 📉 **Overlap Detection** | Detects stock overlap between similar funds |
| ⚠️ **Risk Indicators** | AMC concentration and equity/debt balance check |
| 🎯 **Demo Mode** | Test instantly without a real CAS PDF |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **AI Engine** | Groq API — LLaMA 3.3 70B Versatile |
| **PDF Parser** | casparser |
| **Data Processing** | pandas |
| **Charts** | Plotly |
| **Environment** | python-dotenv |

---

## 📁 Project Structure

```
mf-portfolio-xray/
├── app.py          # Main Streamlit application
├── analyzer.py     # Groq AI integration and analysis functions
├── prompts.py      # All AI prompt templates
├── parser.py       # CAS PDF parsing logic
├── utils.py        # Helper functions and chart generators
├── .env            # API keys (not committed to GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9 or above
- pip

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/mf-portfolio-xray.git
cd mf-portfolio-xray
```

---

### Step 2: Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install streamlit groq casparser python-dotenv pandas plotly
```

---

### Step 4: Get a Free Groq API Key

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign up for free — no credit card needed
3. Click **API Keys** → **Create API Key**
4. Copy the key

---

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ Never commit your `.env` file to GitHub. It is already listed in `.gitignore`.

---

### Step 6: Run the Application

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## 🚀 How to Use

### Option A — Demo Mode (No PDF needed)
1. Open the app at `http://localhost:8501`
2. Click **"🎯 Load Demo Portfolio"** in the sidebar
3. View the full AI analysis for a sample portfolio (Rahul Sharma)

### Option B — Real CAS PDF
1. Get your CAS PDF from **[camsonline.com](https://www.camsonline.com)**
   - Go to Investor Services → Statement → Consolidated Account Statement
   - Enter your PAN and registered email
   - You will receive the PDF in your email
   - Password = your registered email address
2. Upload the PDF in the sidebar
3. Enter your email as the PDF password
4. Click **"🚀 Analyze Portfolio"**

---

## 📊 What the Analysis Shows

### 1. Portfolio Metrics
- Net Worth (current value)
- Total Input Capital (amount invested)
- Current Returns (absolute %)
- Portfolio XIRR (estimated)

### 2. Strategy Drift Chart
- Current allocation vs AI-recommended allocation
- Required modifications per category (Large Cap, Mid Cap, ELSS, Debt etc.)

### 3. Health Indicators
- Portfolio Health Score out of 100
- Risk Exposure meter (Safe → Balanced → Aggressive)
- Fund overlap detection with overlap percentage

### 4. Asset Distribution
- Current portfolio donut chart
- AI-optimized target allocation donut chart

### 5. Fund Holdings Table
- Fund name, AMC, category badge
- Invested amount, current value, growth %
- Green = best performer, Red = worst performer

### 6. Benchmark Comparison
- Your portfolio return vs Nifty 50 (14% avg)
- Visual bar chart comparison

### 7. Strategic Insights
- Key risk indicators with severity levels
- Recommended actions with priority tags
- AI-powered rebalancing suggestions

### 8. AI Verdict
- Full analysis powered by Groq LLaMA 3.3 70B
- Investment summary, best/worst fund, Nifty comparison, one-line verdict

---

## 🔑 API Keys & Cost

| Service | Cost | Limit |
|---|---|---|
| **Groq API** | Free | 14,400 requests/day |
| **casparser** | Free | Open source |
| **Streamlit** | Free | Open source |

> 💡 This project runs entirely on **free APIs** — no credit card required.

---

## 🧪 Sample Output

```
## 1. Investment Summary
- Total Amount Invested: Rs. 12,45,890.00
- Total Current Value:   Rs. 14,41,614.80
- Absolute Gain:         Rs. 1,95,724.80

## 2. Overall Absolute Return
- Formula: ((14,41,614.80 - 12,45,890.00) / 12,45,890.00) x 100
- Result: 15.71%

## 3. Best & Worst Fund
- Best:  HDFC Mid-Cap Opportunities Fund — 17.71%
- Worst: SBI Blue Chip Fund — 13.17%

## 4. Nifty 50 Comparison
- Portfolio: 15.71% vs Nifty 50: 14.00%
- ▲ Beating Nifty by 1.71%

## 5. Verdict
**This portfolio is performing WELL — beating the Nifty 50 benchmark
by 1.71%, led by strong mid-cap performance, though AMC concentration
in HDFC (47%) poses a risk that should be addressed.**
```

---

## ⚠️ Known Limitations

- casparser only works with official **CAMS and Kfintech** CAS PDFs
- XIRR calculation requires transaction dates (estimated if not available)
- AI verdict is for **informational purposes only** — not financial advice

---

## 🤝 Contributing

Pull requests are welcome. For major changes please open an issue first.

---

## 📄 License

MIT License — free to use and modify.

---

## 👨‍💻 Author

Built with ❤️ for the Unstop Hackathon

---

> 🔒 **Privacy Notice:** Your CAS PDF data is processed locally and never stored or transmitted to any server. The only external API call is to Groq for AI text generation — no financial data is sent.
