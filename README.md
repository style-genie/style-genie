# 🔮 StyleRecommendation


**Style Advisor** is an AI‑powered application that helps you discover and try on clothing styles tailored for you:  Snap a selfie or describe your dream look, and the app instantly finds perfectly matched pieces from your favorite brands. Browse a curated selection and virtually try on each item in real time to discover the fit and color that suit you the most, mix, match, and shop with confidence 👗!

---

## 🚀 Key Features
- **Recommendation System using AI-Agents**
  - using the latest stack (fastAPI, CrewAI, Langchain)
  - using Userdata, Vectorsearch, Wikipedia, Websearch, Analytics, Scrapaed Data
  - Agent Workflows that realisticly simulate a fashion consultant
  - get links from the store
  - outfit creator
  - agents are picking items based on pricerange, personal filters (eg jackets only) and modifiers (parameters and prompt instruction)
- **Add your Data**  
  - **Image Upload:** Analyze a user’s photo for style cues.  
  - **Text Prompt:** Accept natural‑language style descriptions (e.g. “boho summer dress”).
  - **Image-Based Analysis:**

- **Virtual Try‑On**  
  - **Virtual Avatar:** Create a personalized avatar from your photo.
  - **Pose‑Aware Warping:** Map garments onto a user’s silhouette using a state‑of‑the‑art try‑on engine.  
  - **Real‑Time Preview:** Instantly see how different pieces look on you.

- **Personalization & Trends**  
  - **User Profiles:** Save favorites, sizes, and style preferences for future sessions.  
  - **Geo & Season Aware:** Recommend items popular in your region or season.

---

## 🛠 Tech Stack

| Layer               | Technology                                 |
|---------------------|--------------------------------------------|
| **Backend API**     | Python · FastAPI ·                         |
| **Agents**          | LiteLLM + CrewAI + LangChain               |
| **Vector Search**   | Pinecone                                   |
| **Object Storage**  | Appache Ozone (s3 Bucket)                  |
| **Database**        | Postgres if needed                         |
| **Virtual Try‑On**  | Flow-Style-VTON                            |
| **Frontend**        | Next.js · React                            |
| **DevOps**          | GH Actions - Docker Compose                |

---

## 🎯 Solutions

### For Fashion Retailers

1. **Personalized Discovery**  
   - Boost engagement by surfacing items tailored to individual tastes   

2. **Trend Insights**  
   - Gather anonymized analytics on popular styles, colors, and body shapes  
   - Adjust inventory and marketing to real‑time demand signals  



### For Customers

1. **Effortless Shopping**  
   - Skip endless browsing—discover outfits that suit your style in seconds  
   - Filter by budget, occasion, and brand preferences  

2. **Try Before You Buy**  
   - Virtual try‑on lets you see how garments fit without stepping into a store  
   - Reduce returns and increase confidence in your purchases  

3. **Consistent Experience**  
   - Save your style profile and revisit personalized recommendations anytime  
   - Mobile‑responsive UI for on‑the‑go styling advice  

---
.
## Quickstart

- clone the repo
  ```bash
  git clone https://github.com/style-genie/style-genie
  ```
- ```bash
  cd style-genie
  ```
### start the backend
- ***with docker***
  - ```bash
    docker compose up
    ```
- ***with local python 3.10***
  - ```bash
    cd ./backend/server
    ```
  - ```bash
    python main.py
    ```
