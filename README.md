# 🎲 Zama Dice Game

> Un jeu de dés moderne avec intégration **Zama FHE** (Fully Homomorphic Encryption) pour des calculs privés sur blockchain.

![Zama Dice Game](https://img.shields.io/badge/Built%20with-Zama%20FHE-purple?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🌟 Fonctionnalités

- 🎲 **Jeu de dés interactif** avec animations fluides
- 🔐 **Zama FHE Integration** - Calculs privés et vérifiables
- 🏆 **Génération NFT** - Métadonnées uniques basées sur les résultats
- 📊 **Statistiques temps réel** - Historique et leaderboards
- 🌐 **Support Sepolia** - Réseau Ethereum de test
- 📱 **Interface responsive** - Mobile, tablette et desktop
- ⚡ **Performance optimisée** - Temps de réponse < 100ms

## 🚀 Déploiement Rapide

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/votre-username/zama-dice-game)

## 🛠️ Stack Technique

- **Frontend:** React 19 + Tailwind CSS + Zama FHE SDK
- **Backend:** FastAPI + Python 3.9+
- **Database:** MongoDB
- **Blockchain:** Sepolia (Ethereum Testnet)
- **Deployment:** Vercel (Recommended)

## 📦 Installation Locale

### Prérequis

- Node.js 18+
- Python 3.9+
- MongoDB (local ou cloud)
- MetaMask extension

### 1. Cloner le repository

```bash
git clone https://github.com/votre-username/zama-dice-game.git
cd zama-dice-game
```

### 2. Configuration Backend

```bash
cd backend
pip install -r requirements.txt
```

Créer `.env` dans le dossier backend :
```env
MONGO_URL=mongodb://localhost:27017/
ZAMA_ENVIRONMENT_ID=ead32e7f-5090-4060-9b60-97f68caa3cf8
```

### 3. Configuration Frontend

```bash
cd frontend
yarn install
```

Créer `.env` dans le dossier frontend :
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 4. Lancement

**Backend:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```bash
cd frontend
yarn start
```

L'application sera disponible sur `http://localhost:3000`

## 🌐 Déploiement sur Vercel

### 1. Fork ce repository sur GitHub

### 2. Connecter à Vercel

1. Aller sur [vercel.com](https://vercel.com)
2. Cliquer "New Project" 
3. Importer votre fork GitHub
4. Vercel détectera automatiquement la configuration

### 3. Variables d'environnement

Dans les settings Vercel, ajouter :

```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/zama_dice_game
REACT_APP_BACKEND_URL=https://votre-app.vercel.app
ZAMA_ENVIRONMENT_ID=ead32e7f-5090-4060-9b60-97f68caa3cf8
```

### 4. Déployer

Vercel déploiera automatiquement à chaque push sur la branche main.

## 🔧 Configuration MongoDB

### Option 1: MongoDB Atlas (Recommandé)

1. Créer un compte sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créer un cluster gratuit
3. Obtenir la connection string
4. Remplacer `MONGO_URL` dans les variables d'environnement

### Option 2: MongoDB Local

```bash
# Installation MongoDB
# MacOS
brew install mongodb-community

# Ubuntu
sudo apt-get install mongodb

# Démarrer MongoDB
mongod
```

## 🎮 Utilisation

### Mode Standard
- Lancer des dés sans connexion wallet
- Résultats générés aléatoirement
- Historique sauvegardé

### Mode FHE (avec wallet)
1. Connecter MetaMask
2. Basculer vers Sepolia testnet
3. Les calculs de dés sont chiffrés avec Zama FHE
4. NFTs générés avec métadonnées spéciales

## 🔐 Intégration Zama FHE

Cette application utilise Zama FHE pour :

- **Calculs privés** : Les résultats de dés sont chiffrés
- **Vérifiabilité** : Impossible de tricher ou manipuler
- **Privacy-preserving** : Les données restent confidentielles
- **Blockchain ready** : Compatible avec les smart contracts

### Environment ID

L'application utilise l'environment ID : `ead32e7f-5090-4060-9b60-97f68caa3cf8`

## 📁 Structure du Projet

```
zama-dice-game/
├── frontend/                 # Application React
│   ├── src/
│   │   ├── App.js           # Composant principal
│   │   ├── App.css          # Styles et animations
│   │   └── ...
│   ├── package.json
│   └── .env
├── backend/                  # API FastAPI
│   ├── server.py            # Serveur principal
│   ├── requirements.txt
│   └── .env
├── api/                      # Vercel serverless functions
│   └── index.py
├── vercel.json              # Configuration Vercel
├── .env.example             # Template variables d'environnement
└── README.md
```

## 🧪 Tests

```bash
# Tests backend
cd backend
python backend_test.py

# Tests frontend
cd frontend
yarn test
```

## 📊 API Endpoints

### Games
- `POST /api/play` - Jouer une partie
- `GET /api/games` - Historique des jeux
- `GET /api/game/{id}` - Détails d'un jeu
- `GET /api/stats` - Statistiques globales

### Users
- `POST /api/user` - Créer/Mettre à jour utilisateur
- `GET /api/user/{address}` - Profil utilisateur
- `GET /api/leaderboard` - Classement

### Health
- `GET /api/health` - Status de l'API

## 🔒 Sécurité

- ✅ Rate limiting (10 req/min)
- ✅ Validation stricte des entrées
- ✅ Sanitisation des données
- ✅ CORS configuré
- ✅ Variables d'environnement sécurisées

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 License

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

## 👨‍💻 Auteur

**@0xDropxtor**
- Twitter: [@0xDropxtor](https://x.com/0xDropxtor)
- GitHub: [@dropxtor](https://github.com/dropxtor)

## 🙏 Remerciements

- [Zama](https://zama.ai) pour la technologie FHE
- [Vercel](https://vercel.com) pour l'hébergement
- [Tailwind CSS](https://tailwindcss.com) pour le design
- Communauté blockchain pour le support

---

⭐ **N'oubliez pas de star le repo si vous l'appréciez !**