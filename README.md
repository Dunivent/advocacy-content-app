**README.md**

# Advocacy & Outreach Content Generator

A Streamlit-powered AI app that helps advocacy organizations generate locally-relevant content using trusted public datasets and OpenAI's language models.

## 🌐 Live App (If Deployed)
[Launch App](https://share.streamlit.io/your-deployment-link)

## 🚀 Features
- Choose issue and geography (state + county)
- Focus areas: Raise Awareness, Take Action, Outreach Support
- Auto-fetches trusted data:
  - Housing (U.S. Census API)
  - Health (CDC PLACES)
  - Food Access (USDA Atlas)
  - Environment (EPA EJSCREEN)
- Generates:
  - Policy brief
  - Social media post
  - Email to supporters
- Schedule and send via social or email

## 🌐 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/advocacy-content-app.git
cd advocacy-content-app
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Add a `.env` File
Create a file named `.env` in the root of the project:
```env
OPENAI_API_KEY=your-openai-key
CENSUS_API_KEY=your-census-key
```

### 4. Run the App
```bash
streamlit run streamlit_app_all_categories_with_env.py
```

### 5. Optional: Deploy to Streamlit Cloud
- Push this repo to GitHub
- Connect to [streamlit.io/cloud](https://streamlit.io/cloud)
- Set the main app file and add secrets via the UI

---
