![banner](https://capsule-render.vercel.app/api?type=waving\&height=250\&color=0:22c55e,100:047857\&text=HalalFit\&fontSize=70\&fontAlign=50\&fontAlignY=40\&animation=fadeIn\&desc=Eat%20Halal.%20Eat%20Healthy.%20Eat%20with%20Confidence.\&descAlignY=60)

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=23&duration=3000&color=22C55E&center=true&vCenter=true&width=900&lines=Smart+Halal+and+Healthy+Food+Assistant;Check+Ingredients+Barcodes+and+Food+Products;Built+for+Safer+and+Healthier+Food+Choices" alt="Typing SVG" />
</p>

---

## 🌐 Live Demo

### [Visit HalalFit](https://halalfit.netlify.app/)

For source code access, collaboration, or project inquiries, contact me through GitHub or email.

---

# 🧠 Platform Overview

**HalalFit** is a smart halal and healthy food assistant that helps users understand whether a food product is suitable for consumption.

The platform can analyze:

* Product names
* Ingredient lists
* Food additives
* E-numbers
* Barcode information
* Product images
* Nutrition information

HalalFit provides two separate results:

1. **Halal Status**
2. **Health Status**

The main goal is to help users make safer, healthier, and more informed food choices.

> **Eat halal. Eat healthy. Eat with confidence.**

---

# ⚡ Core Features

## 🕌 Halal Status Detection

HalalFit classifies products into four main categories:

| Status                 | Meaning                                      |
| ---------------------- | -------------------------------------------- |
| ✅ Halal                | No prohibited ingredient was detected        |
| ❌ Haram                | A clearly prohibited ingredient was detected |
| ⚠️ Doubtful / Mushbooh | The ingredient source is unclear             |
| ❓ Unknown              | There is not enough information to decide    |

The system avoids marking a product as haram without reliable evidence.

---

## ❤️ Health Status Analysis

HalalFit also evaluates the nutritional quality of a product.

The health analysis may check:

* Sugar level
* Salt level
* Saturated fat
* Trans fat
* Calories
* Artificial additives
* Preservatives
* Allergens
* Nutrition score

Possible health results include:

| Status       | Meaning                                    |
| ------------ | ------------------------------------------ |
| 🟢 Healthy   | Generally suitable for regular consumption |
| 🟡 Moderate  | Should be consumed carefully               |
| 🔴 Unhealthy | Contains high-risk nutritional values      |
| ⚪ Unknown    | Nutrition information is unavailable       |

---

## 📷 Camera Ingredient Scanner

Users can capture an image of a product label.

The system uses OCR technology to:

1. Read text from the image
2. Detect the ingredient list
3. Identify suspicious ingredients
4. Analyze halal status
5. Analyze health status
6. Display the final result

---

## 📊 Barcode Scanner

Users can scan a product barcode to:

* Find product information
* Retrieve saved ingredients
* View halal status
* View health information
* Check previous community reports
* Submit missing product information

---

## 🔍 Ingredient Search

Users can manually search for:

* Food ingredients
* Food additives
* E-numbers
* Preservatives
* Flavourings
* Enzymes
* Emulsifiers
* Colouring agents

Example ingredients:

* Gelatin
* E120
* E471
* E472
* Pepsin
* Rennet
* Lard
* Alcohol
* Mono- and diglycerides
* Animal-derived enzymes
* Natural flavouring

---

# 🧭 System Architecture

```mermaid
flowchart LR
    User --> MobileApp
    Admin --> AdminDashboard

    MobileApp --> API
    AdminDashboard --> API

    API --> AuthService
    API --> ProductService
    API --> IngredientService
    API --> HalalAnalysisService
    API --> HealthAnalysisService
    API --> BarcodeService
    API --> OCRService
    API --> ReportService

    ProductService --> Database
    IngredientService --> Database
    HalalAnalysisService --> RulesDatabase
    HealthAnalysisService --> NutritionDatabase
    BarcodeService --> ExternalProductAPI
    OCRService --> ImageProcessingService
    ReportService --> Database

    API --> CloudStorage
```

---

# 🏗 Technology Stack

## Frontend

* Next.js
* TypeScript
* React
* CSS / Tailwind CSS
* Responsive web design

## Backend

* FastAPI
* Python
* REST API
* Role-based API authorization
* API validation and error handling

## Database

* PostgreSQL
* Neon Serverless PostgreSQL

## Deployment

* Frontend deployment: `[Add your frontend hosting platform]`
* Backend deployment: `[Add your backend hosting platform]`
* Cloud database: Neon

---

# 🧭 System Architecture

```mermaid
flowchart LR
    User --> NextJSFrontend
    Admin --> NextJSFrontend

    NextJSFrontend --> FastAPIBackend

    FastAPIBackend --> AuthenticationService
    FastAPIBackend --> ProductService
    FastAPIBackend --> IngredientService
    FastAPIBackend --> HalalAnalysisService
    FastAPIBackend --> HealthAnalysisService
    FastAPIBackend --> ReportService

    AuthenticationService --> NeonPostgreSQL
    ProductService --> NeonPostgreSQL
    IngredientService --> NeonPostgreSQL
    HalalAnalysisService --> NeonPostgreSQL
    HealthAnalysisService --> NeonPostgreSQL
    ReportService --> NeonPostgreSQL
```

---

# 📂 Project Structure

```text
HalalFit
│
├── frontend
│   ├── app
│   │   ├── dashboard
│   │   ├── products
│   │   ├── ingredients
│   │   ├── analysis
│   │   ├── reports
│   │   ├── profile
│   │   ├── login
│   │   └── register
│   │
│   ├── components
│   ├── services
│   ├── hooks
│   ├── types
│   ├── public
│   ├── package.json
│   └── tsconfig.json
│
├── backend
│   ├── app
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models
│   │   ├── schemas
│   │   ├── routes
│   │   ├── services
│   │   ├── dependencies
│   │   └── utilities
│   │
│   ├── requirements.txt
│   └── .env
│
├── README.md
└── .gitignore
```

> Update the folder names above so they match your actual project structure.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/HalalFit.git
cd HalalFit
```

---

## 2. Configure the Frontend

```bash
cd frontend
npm install
```

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Run the Next.js development server:

```bash
npm run dev
```

The frontend will normally run at:

```text
http://localhost:3000
```

---

## 3. Configure the FastAPI Backend

Open another terminal:

```bash
cd backend
```

Create a Python virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux or macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

---

## 4. Configure the Neon PostgreSQL Database

Create a `.env` file inside the backend directory:

```env
DATABASE_URL=your_neon_postgresql_connection_string
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Example Neon connection format:

```env
DATABASE_URL=postgresql://username:password@hostname/database?sslmode=require
```

Do not publish your real database URL or secret key on GitHub.

---

## 5. Run the FastAPI Backend

```bash
uvicorn app.main:app --reload
```

The backend will normally run at:

```text
http://localhost:8000
```

FastAPI documentation will be available at:

```text
http://localhost:8000/docs
```

Alternative API documentation:

```text
http://localhost:8000/redoc
```

---

# 🔌 API Structure

## Authentication

```http
POST /auth/register
POST /auth/login
GET  /auth/me
```

## Products

```http
GET    /products
GET    /products/{product_id}
POST   /products
PUT    /products/{product_id}
DELETE /products/{product_id}
```

## Ingredients

```http
GET    /ingredients
GET    /ingredients/{ingredient_id}
POST   /ingredients
PUT    /ingredients/{ingredient_id}
DELETE /ingredients/{ingredient_id}
```

## Halal Analysis

```http
POST /analysis/ingredients
POST /analysis/product
```

## User Reports

```http
POST /reports
GET  /reports
PUT  /reports/{report_id}
```

> Replace these example endpoints with the routes used by your actual FastAPI backend.

---

# 🗄 Database Overview

HalalFit uses **PostgreSQL**, hosted on the **Neon cloud database platform**.

The database may contain information about:

* Users
* Products
* Ingredients
* Food additives
* E-numbers
* Halal classifications
* Health classifications
* Product reports
* Saved products
* Search history
* Review records

```mermaid
erDiagram
    USERS ||--o{ REPORTS : creates
    USERS ||--o{ SAVED_PRODUCTS : saves
    PRODUCTS ||--o{ REPORTS : receives
    PRODUCTS ||--o{ PRODUCT_INGREDIENTS : contains
    INGREDIENTS ||--o{ PRODUCT_INGREDIENTS : belongs_to

    USERS {
        int id
        string name
        string email
        string role
    }

    PRODUCTS {
        int id
        string name
        string barcode
        string halal_status
        string health_status
    }

    INGREDIENTS {
        int id
        string name
        string halal_status
        string explanation
    }

    REPORTS {
        int id
        int user_id
        int product_id
        string reason
        string status
    }
```

---

# 🔒 Security

The platform should protect sensitive information using:

* Secure authentication
* Password hashing
* Role-based access control
* Protected FastAPI routes
* Request validation
* Environment variables
* Database connection encryption
* Input validation
* Error handling
* Secure Neon PostgreSQL connection

Sensitive information must never be committed to GitHub.

Add these files to `.gitignore`:

```gitignore
.env
.env.local
venv/
__pycache__/
node_modules/
.next/
```

---

# 🚀 Deployment Architecture

```mermaid
flowchart LR
    Browser --> NextJSApplication
    NextJSApplication --> FastAPIApplication
    FastAPIApplication --> NeonDatabase

    subgraph Frontend
        NextJSApplication
    end

    subgraph Backend
        FastAPIApplication
    end

    subgraph CloudDatabase
        NeonDatabase
    end
```

---

# 🏗 Correct Stack Summary

| Layer                   | Technology |
| ----------------------- | ---------- |
| Frontend                | Next.js    |
| Frontend language       | TypeScript |
| UI library              | React      |
| Backend                 | FastAPI    |
| Backend language        | Python     |
| Database                | PostgreSQL |
| Cloud database provider | Neon       |
| API style               | REST API   |


# 🌍 Supported Languages

Planned language support:

* English
* বাংলা
* العربية
* اردو
* Bahasa Indonesia
* Bahasa Melayu

---

# 🚀 Future Vision

* AI-assisted ingredient analysis
* Multilingual OCR
* Global halal-certification database
* Manufacturer verification system
* Community product reviews
* Nearby halal-food discovery
* Restaurant halal verification
* Personal dietary preferences
* Allergy warnings
* Diabetes-friendly product analysis
* Heart-health recommendations
* Offline barcode scanning
* Smart shopping lists
* Family accounts
* Scholar and expert review panel
* Halal certification expiry alerts

---

# ⚠️ Important Disclaimer

HalalFit is an informational platform.

The application does not replace:

* Qualified Islamic scholars
* Recognized halal-certification authorities
* Doctors
* Dietitians
* Medical professionals

Halal classifications depend on the quality of available product and ingredient information.

Users should verify doubtful products with a trusted halal-certification authority or qualified scholar.

Health information is provided for general educational purposes and should not be treated as medical advice.

---

# 🤝 Contributing

Contributions are welcome.

To contribute:

```bash
git checkout -b feature/your-feature-name
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

Then create a pull request.

Before submitting a contribution:

* Follow the project coding standards
* Test your changes
* Do not add unverified halal rulings
* Include reliable references for ingredient classifications
* Keep health information evidence-based
* Explain major changes clearly

---

# 🐛 Reporting Issues

When reporting an issue, include:

* Issue description
* Steps to reproduce
* Expected result
* Actual result
* Device or browser information
* Screenshots, when available

For incorrect halal or health information, also include:

* Product name
* Barcode
* Ingredient image
* Country
* Certification information
* Reliable supporting source

---

# 📜 License

This project is licensed under the MIT License.

See the `LICENSE` file for more information.

---

# 👨‍💻 Author

**Md Mahruf Alam**

Software Engineer
Full-Stack Developer
System Architect
Problem Solver

### Contact

* GitHub: [minisowad](https://github.com/miniSOWAD)
* LinkedIn: [Mahruf Alam](https://www.linkedin.com/in/md-mahruf-alam-sowad-397aaa309/)
* Email: `your-email@example.com`

---

# ⭐ Support the Project

If you find HalalFit useful:

* Give the repository a star
* Share the project
* Report incorrect product information
* Suggest new features
* Contribute to the codebase

<p align="center">
  <strong>HalalFit</strong>
  <br />
  Eat halal. Eat healthy. Eat with confidence.
</p>

![footer](https://capsule-render.vercel.app/api?type=waving\&height=150\&color=0:047857,100:22c55e\&section=footer)
