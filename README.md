# 🛍️ WhatsApp E-Commerce Shopping Assistant

An intelligent **AI-powered shopping assistant** that enables customers to browse products, manage their cart, and place orders through **WhatsApp** or a **web interface**.  
Built with **LangGraph multi-agent architecture**, **Salesforce CRM integration**, and **real-time cart synchronization**.

---

## ✨ Features

### 🤖 AI-Powered Conversational Shopping
- Natural language product search with intelligent query interpretation  
- Context-aware conversation handling  
- Multi-intent support within single conversations  

### 🛒 Complete E-Commerce Functionality
- **Product Browsing:** Search with filters (color, size, price, category)  
- **Cart Management:** Add, remove, and update quantities in real-time  
- **Order Placement:** Seamless checkout with customer information collection  
- **Order Tracking:** Look up order status by order number or email  

### 📱 Dual Interface
- **WhatsApp Bot:** Chat-based shopping via Twilio integration  
- **Web Application:** Modern React frontend with Shadcn UI  

### 🔄 Real-Time Synchronization
- Cart sync between WhatsApp and web interfaces  
- Session linking across platforms  
- Persistent conversation history with MongoDB  

### 🏢 Salesforce CRM Integration
- Product catalog management  
- Customer account creation and updates  
- Order processing and tracking  
- Pricebook management  

### 🎯 Advanced Agent Architecture
- **Supervisor Multi-Agent System:** Intelligent task delegation  
- **Specialized Sub-Agents:**
  - 🔍 **Search Agent:** Product discovery and filtering  
  - 🛒 **Cart Agent:** Shopping cart operations  
  - 💳 **Checkout Agent:** Order placement workflow  
  - 📦 **Tracking Agent:** Order status lookup

## ⚙️ Key Components

### 🖥️ Frontend (React + Vite)
- Modern UI with **Shadcn** components  
- Real-time cart updates  
- Fully responsive design  

### 🧠 Backend Services
- **Main API:** RESTful endpoints for products, cart, and orders  
- **WhatsApp Server:** Webhook handler for Twilio messages  
- **MCP Server:** Tool server for agent operations  

### 🤖 Agent System
- **Supervisor:** Orchestrates sub-agents using **LangGraph**  
- **Sub-Agents:** Specialized agents for specific tasks  
- **State Management:** Persistent conversation context across sessions  

### 🌐 External Integrations
- **Salesforce:** Product and order management  
- **MongoDB Atlas:** Conversation history and sessions  
- **Twilio:** WhatsApp messaging integration  
- **OpenAI:** LLM for natural language understanding  

---

## 🛠️ Tech Stack

### 🧩 Backend
- **Python 3.11+**  
- **FastAPI:** High-performance async web framework  
- **LangChain & LangGraph:** Agent orchestration  
- **FastMCP:** Model Context Protocol server  
- **Simple-Salesforce:** Salesforce API client  
- **Twilio:** WhatsApp messaging SDK  
- **PyMongo:** MongoDB driver  

### 💻 Frontend
- **React 18:** Modern UI library  
- **TypeScript:** Type-safe JavaScript  
- **Vite:** Ultra-fast build tool  
- **Shadcn/ui:** UI component library  
- **TailwindCSS:** Utility-first CSS framework  

### 🧱 Infrastructure
- **Docker & Docker Compose:** Containerization and orchestration  
- **MongoDB Atlas:** Cloud-hosted database  
- **Ngrok:** Secure webhook tunneling  
- **Uvicorn:** ASGI server for FastAPI  

### 🧬 AI / ML
- **OpenAI GPT-4:** Core language model  
- **LangChain:** LLM orchestration framework  
- **LangGraph:** Multi-agent workflow management  

---

## 📂 Project Structure

```bash
whatsapp-e-commerce-assistant/
├── backend/
│   ├── agents.py              # Multi-agent implementation
│   ├── graph.py               # LangGraph workflow
│   ├── main.py                # Main API server
│   ├── mcp_server.py          # MCP tool server
│   ├── mcp_client.py          # MCP client wrapper
│   ├── whatsapp_server.py     # WhatsApp webhook server
│   ├── state.py               # State management
│   ├── mongodb_config.py      # Database configuration
│   └── test.py                # Test suite
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── lib/               # Utilities
│   │   └── App.tsx            # Main app component
│   ├── package.json
│   └── vite.config.ts
├── salesforce/
│   ├── client.py              # Salesforce client
│   └── schema.py              # Data models
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── Dockerfile.backend         # Backend Docker image
├── Dockerfile.frontend        # Frontend Docker image
├── docker-compose.yml         # Docker orchestration
└── README.md                  # Project documentation
```
## 📋 Prerequisites

### 🧑‍💻 For Local Development
- **Python 3.11+**
- **Node.js 18+** and **npm**
- **MongoDB Atlas account** (free tier works)
- **Salesforce Developer Account**
- **OpenAI API key**
- **Twilio Account** (for WhatsApp)
- **Ngrok Account** (for webhook tunneling)

### 🐳 For Docker Deployment
- **Docker Desktop** or **Docker Engine**
- **Docker Compose**
- All the accounts mentioned above

---

## 🚀 Installation

### ⚙️ Option 1: Running Locally

#### 1. Clone the Repository

- git clone https://github.com/yourusername/whatsapp-ecommerce-assistant.git
- cd whatsapp-ecommerce-assistant
### 2. Set Up Backend

- Create virtual environment
- python -m venv venv

### Activate virtual environment
- On Windows:
- venv\Scripts\activate
### On macOS/Linux:
- source venv/bin/activate

### Install dependencies
- pip install -r requirements.txt
### 3. Set Up Frontend
- cd frontend
- npm install
cd ..
### 4. Configure Environment Variables
- Create a .env file in the project root:


### Salesforce Configuration
- SALESFORCE_USERNAME=your_salesforce_username
- SALESFORCE_PASSWORD=your_salesforce_password
- SALESFORCE_SECURITY_TOKEN=your_security_token

### OpenAI Configuration
- OPENAI_API_KEY=your_openai_api_key

### Twilio Configuration
- TWILIO_ACCOUNT_SID=your_twilio_account_sid
- TWILIO_AUTH_TOKEN=your_twilio_auth_token
- TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

### MongoDB Atlas
- MONGODB_URI=mongodb+srv:
- MONGODB_DB=whatsapp_shopping

### Ngrok (get from https://ngrok.com)
- NGROK_AUTHTOKEN=your_ngrok_auth_token

### API Configuration
- MAIN_API_URL=http://localhost:8000/api
5. Start Services (5 Terminals)

### Terminal 1: MCP Server
- cd backend
- python mcp_server.py

### Terminal 2: Main API
- cd backend
- python main.py

### Terminal 3: WhatsApp Server
- cd backend
- python whatsapp_server.py

### Terminal 4: Ngrok
- ngrok http 5000

### Terminal 5: Frontend
- cd frontend
- npm run dev
### 6. Configure Twilio Webhook
- Copy the HTTPS URL from Ngrok (Terminal 4)

- Go to Twilio WhatsApp Sandbox

- Paste the URL with the /webhook endpoint:

- https://YOUR_NGROK_URL.ngrok.io/webhook
- Save the configuration


### 7. Access the Application
- Service	URL	Description
- 🖥️ Frontend	http://localhost:8080
- 	Web Interface
- 📘 API Docs	http://localhost:8000/docs
- 	Swagger UI
- ⚙️ Main API	http://localhost:8000
- 	REST API
- 💬 WhatsApp	WhatsApp Chat	Send a message to your Twilio number


### 🐳 Option 2: Running with Docker
### 1. Clone the Repository
- git clone https://github.com/yourusername/whatsapp-ecommerce-assistant.git
- cd whatsapp-ecommerce-assistant

###2. Configure Environment Variables

- Create a .env file (same as in local setup).
- Make sure to include your Ngrok Auth Token:

- NGROK_AUTHTOKEN=your_ngrok_auth_token

### 3. Build Docker Images
- docker-compose build


- This will build:

- 🧠 Backend image: MCP Server, Main API, WhatsApp Server

- 💻 Frontend image: React + Vite

### 4. Start All Services
- docker-compose up -d


- This starts:

- ✅ Backend container (ports 8001, 8000, 5000)

- ✅ Frontend container (port 8080)

- ✅ Ngrok container (port 4040)

### 5. Get Ngrok URL

- Option A: Web Interface

- http://localhost:4040


- Option B: Command Line

### Windows PowerShell
- (Invoke-WebRequest -Uri "http://localhost:4040/api/tunnels" | ConvertFrom-Json).tunnels[0].public_url

### macOS/Linux
- curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'

### 6. Configure Twilio Webhook

- Copy the HTTPS URL and append /webhook:

- https://YOUR_NGROK_URL.ngrok.io/webhook


- Paste this URL into your Twilio WhatsApp Sandbox Settings.

### 7. Verify Services
### Check container status
- docker-compose ps

### View logs
- docker-compose logs -f

### Test Main API
- curl http://localhost:8000/health

### Test WhatsApp Server
- curl http://localhost:5000/

### 8. Access the Application
- Service	URL	Description
- 🖥️ Frontend	http://localhost:8080
- 	Web UI
- 📘 API Docs	http://localhost:8000/docs
- 	Swagger UI
- ⚙️ Main API	http://localhost:8000
- 	REST API
- 🧩 MCP Server	http://localhost:8001
- 	Tool Server
- 💬 WhatsApp	http://localhost:5000
- 	Webhook Handler
- 🌐 Ngrok Dashboard	http://localhost:4040
- 	Tunnel Status


## ⚙️ Configuration

### 🗄️ MongoDB Atlas Setup
1. Create a **free cluster** on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)  
2. Create a **database user**  
3. **Whitelist your IP address** (or use `0.0.0.0/0` for development)  
4. Get your **connection string**  
5. Add the following to your `.env` file:
   ```env
   MONGODB_URI=mongodb+srv:
   MONGODB_DB=whatsapp_shopping
### 🏢 Salesforce Setup
- Sign up for a Salesforce Developer Account at developer.salesforce.com

- Create custom fields on Product2:

- Color__c (Text)

- Size__c (Text)

- Image_URL__c (URL)

- Get your security token from Salesforce Settings

- Add your Salesforce credentials to .env

### 💬 Twilio WhatsApp Setup
- Sign up at Twilio

- Activate your WhatsApp Sandbox

- Get your Account SID and Auth Token

- Add them to .env:

- env
- TWILIO_ACCOUNT_SID=your_twilio_account_sid
- TWILIO_AUTH_TOKEN=your_twilio_auth_token
- TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
- Configure the webhook URL from your Ngrok instance (e.g. https://YOUR_NGROK_URL.ngrok.io/webhook)

### 🌐 Ngrok Setup
- Sign up at Ngrok

- Get your auth token from the Ngrok dashboard

- Add it to .env:

- env

- NGROK_AUTHTOKEN=your_token_here
# 📱 Usage
### 🖥️ Web Interface
### 🛍️ Browse Products
- Navigate to http://localhost:8080

- Use search and filters to find products
- View detailed product information

### 🛒 Manage Cart
- Add products to your cart

- Update quantities in real-time

- Remove unwanted items

### 💳 Checkout
- Fill in customer details (name, email, phone)

- Review your order summary

- Place the order seamlessly

###  🧑‍💼 Admin Panel
- Manage product inventory (CRUD operations)
- View session-specific products
- Track order history and status

- 💬 WhatsApp Bot
- Send messages to your Twilio WhatsApp number and start chatting with your AI shopping assistant.

### 🗣️ Example Conversations
- User:

- Hello

- Bot:

- Hey! 👋 I'm your shopping assistant! I can help you browse, manage your cart, or place an order.

- User:

- Show me silver watches

- Bot:

- Here are 3 great watches for you:
- 1️⃣ Chronograph Watch - $129.99
- 2️⃣ Classic Silver - $99.50
- 3️⃣ Titan Edge - $149.00

- User:

- Add option 1

- Bot:

- ✅ Added Chronograph Watch to your cart!
- 🛒 Your Cart: 1 item - Total $129.99

- User:

- Checkout

- Bot:

- Great! Let's complete your order 🎉
- To proceed, I need the following details:
- 📝 Full Name
- 📧 Email Address
- 📱 Phone Number

- User:

- John Doe, john@email.com, +1234567890

- Bot:

- 📋 Order Confirmation
- 🛍️ Items: Chronograph Watch
- 💵 Total: $129.99
- Say ‘Yes’ to confirm your order

- User:

- Yes

- Bot:

- 🎉 Order Confirmed!
- ✅ Order Number: #00001234
