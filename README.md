# 🧭 Career Guidance System

A web-based career guidance tool that helps students and professionals discover career paths that align with their interests, strengths, and preferences.

## ✨ Features

- **Personalised Quiz** – Answer 6 questions to receive your top 3 career matches with percentage-based match scores
- **Career Profiles** – 8 detailed career profiles covering salary ranges, job growth, education, and required skills
- **Learning Resources** – Curated links to courses, certifications, and communities for each career
- **Browse & Filter** – Search and filter careers by category (Technology, Analytical, Creative, Social)
- **Career Detail Modal** – Click any career card for an in-depth view
- **Responsive Design** – Works on desktop, tablet, and mobile

## 🗂 Project Structure

```
career-guidance-system/
├── index.html          # Main application page
├── css/
│   └── style.css       # Application stylesheet
├── js/
│   └── app.js          # Quiz logic, career matching & UI
├── data/
│   └── careers.json    # Career data and quiz questions
└── README.md
```

## 🚀 Getting Started

Because the app uses the Fetch API to load `data/careers.json`, you need to serve it from a local web server rather than opening the file directly.

### Option 1 – Python (no install required)

```bash
# Python 3
python -m http.server 8080
```

Then open [http://localhost:8080](http://localhost:8080) in your browser.

### Option 2 – Node.js (`npx serve`)

```bash
npx serve .
```

### Option 3 – VS Code Live Server

Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension and click **Go Live**.

## 🧠 How the Matching Works

Each quiz answer maps to one or more career categories (`technology`, `analytical`, `creative`, `social`). After all 6 questions, each career is scored by how many of its categories appear in your answers. The top 3 highest-scoring careers are displayed as your personalised recommendations.

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Markup | HTML5 |
| Styling | CSS3 (custom properties, grid, flexbox, animations) |
| Logic | Vanilla JavaScript (ES6+, Fetch API) |
| Data | JSON |

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
