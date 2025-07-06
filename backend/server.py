from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime, timedelta
import random
import json
import time

app = FastAPI()

# Rate limiting dictionary
rate_limit_store = {}

def rate_limit(request: Request, max_requests: int = 30, window_seconds: int = 60):
    """Simple rate limiting implementation"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old entries
    rate_limit_store[client_ip] = [
        timestamp for timestamp in rate_limit_store.get(client_ip, [])
        if current_time - timestamp < window_seconds
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store.get(client_ip, [])) >= max_requests:
        return False
    
    # Add current request
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    rate_limit_store[client_ip].append(current_time)
    
    return True

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = AsyncIOMotorClient(MONGO_URL)
db = client['zama_dice_game']
games_collection = db['games']
users_collection = db['users']
nfts_collection = db['nfts']

# Pydantic models
class GameResult(BaseModel):
    id: str
    player_address: Optional[str] = None
    dice_results: List[int]
    total_score: int
    timestamp: datetime
    network: str = "sepolia"
    nft_generated: bool = False
    nft_metadata: Optional[dict] = None
    game_mode: str = "standard"  # "standard" or "fhe"
    environment_id: Optional[str] = None
    fhe_data: Optional[dict] = None

class User(BaseModel):
    id: str
    wallet_address: str
    username: str
    games_played: int = 0
    total_score: int = 0
    nfts_owned: int = 0

class NFTMetadata(BaseModel):
    id: str
    token_id: Optional[str] = None
    owner_address: str
    dice_combination: List[int]
    rarity: str
    image_url: str
    attributes: dict
    created_at: datetime

# Game logic
def roll_dice(num_dice: int = 2) -> List[int]:
    """Roll dice and return results"""
    if num_dice < 1:
        num_dice = 2  # Default to 2 dice if invalid
    return [random.randint(1, 6) for _ in range(num_dice)]

def calculate_score(dice_results: List[int]) -> int:
    """Calculate game score based on dice results"""
    total = sum(dice_results)
    # Bonus for special combinations
    if len(set(dice_results)) == 1:  # All same
        total *= 2
    elif sorted(dice_results) == list(range(min(dice_results), max(dice_results) + 1)):  # Sequence
        total += 10
    return total

def determine_nft_rarity(dice_results: List[int], game_mode: str = "standard") -> str:
    """Determine NFT rarity based on dice results and game mode"""
    if len(set(dice_results)) == 1:  # All same
        return "Legendary" if game_mode == "fhe" else "Epic"
    elif sum(dice_results) >= 10:
        return "Rare" if game_mode == "fhe" else "Uncommon"
    elif sum(dice_results) >= 7:
        return "Uncommon" if game_mode == "fhe" else "Common"
    else:
        return "Common"

def generate_nft_metadata(dice_results: List[int], player_address: str, game_mode: str = "standard") -> dict:
    """Generate NFT metadata based on dice results and game mode"""
    rarity = determine_nft_rarity(dice_results, game_mode)
    
    # Generate unique attributes
    attributes = {
        "dice_combination": dice_results,
        "total_score": sum(dice_results),
        "rarity": rarity,
        "special_combo": len(set(dice_results)) == 1,
        "creator": "dropxtor",
        "network": "sepolia",
        "game_mode": game_mode,
        "fhe_enabled": game_mode == "fhe"
    }
    
    # Generate image URL based on combination and mode
    mode_prefix = "fhe" if game_mode == "fhe" else "std"
    image_url = f"https://api.dicenft.game/images/{mode_prefix}-{'-'.join(map(str, dice_results))}.png"
    
    nft_name = f"{'🔐 FHE ' if game_mode == 'fhe' else ''}Dice NFT #{'-'.join(map(str, dice_results))}"
    description = f"A {'privacy-preserving ' if game_mode == 'fhe' else ''}unique NFT generated from dice roll: {dice_results}. Rarity: {rarity}"
    
    return {
        "name": nft_name,
        "description": description,
        "image": image_url,
        "attributes": attributes,
        "creator": "dropxtor",
        "twitter": "@0xDropxtor",
        "powered_by": "Zama FHE" if game_mode == "fhe" else "Standard RNG"
    }

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "zama-dice-game"}

@app.post("/api/play")
async def play_game(request: Request, player_address: Optional[str] = None, num_dice: int = 2, 
                   game_mode: str = "standard", encrypted_data: Optional[Dict[str, Any]] = None,
                   environment_id: Optional[str] = None):
    """Play a game of dice with optional FHE support"""
    try:
        # Rate limiting
        if not rate_limit(request, max_requests=20, window_seconds=60):
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before making more requests.")
        
        # Validate input
        if num_dice < 1 or num_dice > 6:
            raise HTTPException(status_code=400, detail="Number of dice must be between 1 and 6")
        
        if player_address and not player_address.startswith("0x"):
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Process game based on mode
        if game_mode == "fhe" and encrypted_data:
            print(f"🔐 Processing FHE game with environment ID: {environment_id}")
            
            # For now, we'll simulate FHE processing
            # In a full implementation, you'd decrypt and verify the FHE data
            dice_results = [
                random.randint(1, 6) for _ in range(num_dice)
            ]
            
            # Log FHE processing
            print(f"🎲 FHE encrypted dice data received: {len(encrypted_data.get('dice1', []))} bytes")
            print(f"🎯 Generated dice results: {dice_results}")
            
        else:
            # Standard dice roll
            print(f"🎲 Processing standard game")
            dice_results = roll_dice(num_dice)
        
        total_score = calculate_score(dice_results)
        
        # Generate NFT metadata with game mode
        nft_metadata = None
        nft_generated = False
        
        if player_address:
            nft_metadata = generate_nft_metadata(dice_results, player_address, game_mode)
            nft_generated = True
        
        # Create game result
        game_result = GameResult(
            id=str(uuid.uuid4()),
            player_address=player_address,
            dice_results=dice_results,
            total_score=total_score,
            timestamp=datetime.now(),
            nft_generated=nft_generated,
            nft_metadata=nft_metadata,
            game_mode=game_mode,
            environment_id=environment_id,
            fhe_data={"encrypted": bool(encrypted_data)} if encrypted_data else None
        )
        
        # Save to database
        await games_collection.insert_one(game_result.dict())
        
        return {
            "success": True,
            "game_id": game_result.id,
            "dice_results": dice_results,
            "total_score": total_score,
            "nft_generated": nft_generated,
            "nft_metadata": nft_metadata,
            "network": "sepolia",
            "game_mode": game_mode,
            "fhe_enabled": game_mode == "fhe",
            "environment_id": environment_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/games")
async def get_games(limit: int = 10):
    """Get recent games"""
    try:
        games = await games_collection.find().sort("timestamp", -1).limit(limit).to_list(limit)
        # Convert MongoDB documents to JSON serializable format
        for game in games:
            if '_id' in game:
                del game['_id']
        return {"games": games}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/game/{game_id}")
async def get_game(game_id: str):
    """Get specific game by ID"""
    try:
        game = await games_collection.find_one({"id": game_id})
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        # Convert MongoDB document to JSON serializable format
        if '_id' in game:
            del game['_id']
        return game
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/user")
async def create_user(wallet_address: str, username: str):
    """Create or update user profile"""
    try:
        # Validate input
        if not wallet_address.startswith("0x") or len(wallet_address) != 42:
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        if not username or len(username) < 3 or len(username) > 20:
            raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters")
        
        user = User(
            id=str(uuid.uuid4()),
            wallet_address=wallet_address,
            username=username
        )
        
        # Check if user exists
        existing_user = await users_collection.find_one({"wallet_address": wallet_address})
        if existing_user:
            # Update existing user
            await users_collection.update_one(
                {"wallet_address": wallet_address},
                {"$set": {"username": username}}
            )
            # Convert MongoDB document to JSON serializable format
            if '_id' in existing_user:
                del existing_user['_id']
            return {"success": True, "message": "User updated", "user": existing_user}
        else:
            # Create new user
            await users_collection.insert_one(user.dict())
            return {"success": True, "message": "User created", "user": user.dict()}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/user/{wallet_address}")
async def get_user(wallet_address: str):
    """Get user profile"""
    try:
        user = await users_collection.find_one({"wallet_address": wallet_address})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Convert MongoDB document to JSON serializable format
        if '_id' in user:
            del user['_id']
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top players leaderboard"""
    try:
        # Get top users by total score
        pipeline = [
            {"$group": {
                "_id": "$player_address",
                "total_score": {"$sum": "$total_score"},
                "games_played": {"$sum": 1}
            }},
            {"$sort": {"total_score": -1}},
            {"$limit": limit}
        ]
        
        leaderboard = await games_collection.aggregate(pipeline).to_list(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get game statistics"""
    try:
        total_games = await games_collection.count_documents({})
        total_users = await users_collection.count_documents({})
        total_nfts = await games_collection.count_documents({"nft_generated": True})
        
        return {
            "total_games": total_games,
            "total_users": total_users,
            "total_nfts": total_nfts,
            "network": "sepolia"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)