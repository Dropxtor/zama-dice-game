# 📚 Guide de Déploiement GitHub + Vercel

## 🚀 Instructions Complètes

### Étape 1: Préparation du Repository GitHub

1. **Créer un nouveau repository sur GitHub**
   ```
   - Nom: zama-dice-game
   - Description: Jeu de dés moderne avec Zama FHE
   - Public ou Private (votre choix)
   - README: ✅ (déjà créé)
   - .gitignore: ✅ (déjà configuré)
   - License: MIT ✅ (déjà créé)
   ```

2. **Cloner et pousser le code**
   ```bash
   # Dans votre terminal local, depuis le dossier /app
   git init
   git add .
   git commit -m "🎲 Initial commit - Zama Dice Game v1.0.0"
   git branch -M main
   git remote add origin https://github.com/VOTRE-USERNAME/zama-dice-game.git
   git push -u origin main
   ```

### Étape 2: Configuration MongoDB Atlas

1. **Créer un compte MongoDB Atlas**
   - Aller sur https://www.mongodb.com/cloud/atlas
   - Créer un compte gratuit
   - Créer un nouveau cluster (gratuit M0)

2. **Configuration de sécurité**
   - Database Access: Créer un utilisateur avec mot de passe
   - Network Access: Ajouter 0.0.0.0/0 (toutes IPs)

3. **Obtenir la connection string**
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/zama_dice_game
   ```

### Étape 3: Déploiement sur Vercel

1. **Connecter à Vercel**
   - Aller sur https://vercel.com
   - Se connecter avec GitHub
   - Cliquer "New Project"
   - Importer votre repository `zama-dice-game`

2. **Configuration automatique**
   - Vercel détectera automatiquement:
     - Frontend: React (dossier `/frontend`)
     - API: Python (dossier `/api`)
     - Build settings: `vercel.json`

3. **Variables d'environnement**
   
   Dans Vercel Dashboard > Settings > Environment Variables, ajouter:
   
   **Production:**
   ```
   MONGO_URL = mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/zama_dice_game
   REACT_APP_BACKEND_URL = https://zama-dice-game.vercel.app
   ZAMA_ENVIRONMENT_ID = ead32e7f-5090-4060-9b60-97f68caa3cf8
   NODE_ENV = production
   ```
   
   **Preview/Development:**
   ```
   MONGO_URL = mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/zama_dice_game_dev
   REACT_APP_BACKEND_URL = https://zama-dice-game-git-branch.vercel.app
   ZAMA_ENVIRONMENT_ID = ead32e7f-5090-4060-9b60-97f68caa3cf8
   NODE_ENV = development
   ```

4. **Déployer**
   - Cliquer "Deploy"
   - Attendre 2-3 minutes
   - Votre app sera live sur `https://zama-dice-game.vercel.app`

### Étape 4: Configuration DNS (Optionnel)

Si vous avez un domaine personnalisé:

1. **Dans Vercel Dashboard**
   - Settings > Domains
   - Ajouter votre domaine: `dice.mondomaine.com`

2. **Configuration DNS**
   - Ajouter un CNAME: `dice.mondomaine.com` → `cname.vercel-dns.com`

### Étape 5: Monitoring et Analytics

1. **Vercel Analytics**
   - Settings > Analytics
   - Activer Real Experience Score

2. **Monitoring des erreurs**
   - Settings > Functions
   - Voir les logs des API

### Étape 6: CI/CD avec GitHub Actions (Optionnel)

Le fichier `.github/workflows/deploy.yml` est déjà configuré.

**Pour l'activer:**

1. **Secrets GitHub**
   - Repository Settings > Secrets and variables > Actions
   - Ajouter:
     ```
     VERCEL_TOKEN = (depuis Vercel Settings > Tokens)
     ORG_ID = (depuis Vercel Dashboard)
     PROJECT_ID = (depuis Vercel Project Settings)
     ```

2. **Auto-déploiement**
   - Chaque push sur `main` déclenchera les tests et le déploiement

## ✅ Checklist Post-Déploiement

- [ ] Application accessible via l'URL Vercel
- [ ] API endpoints fonctionnent (`/api/health`)
- [ ] Base de données MongoDB connectée
- [ ] FHE status "Ready" affiché
- [ ] Jeu de dés fonctionne
- [ ] Interface responsive sur mobile
- [ ] Variables d'environnement configurées
- [ ] Domaine personnalisé configuré (si applicable)

## 🔧 Dépannage

### Problème: API ne fonctionne pas
```bash
# Vérifier les logs Vercel
vercel logs

# Vérifier la configuration
cat vercel.json
```

### Problème: MongoDB connexion
```bash
# Tester la connection string
mongosh "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/zama_dice_game"
```

### Problème: Build frontend échoue
```bash
# Localement
cd frontend
yarn build

# Vérifier les dépendances
yarn install --frozen-lockfile
```

### Problème: Variables d'environnement
1. Vérifier que toutes les variables sont définies dans Vercel
2. Redéployer après modification des variables

## 📞 Support

En cas de problème:

1. **Vercel Docs**: https://vercel.com/docs
2. **GitHub Issues**: Créer une issue sur votre repository
3. **Discord communautés**: Vercel Discord, Zama Discord

## 🎉 Félicitations !

Votre **Zama Dice Game** est maintenant déployée et accessible publiquement !

**URL de production**: `https://zama-dice-game.vercel.app`