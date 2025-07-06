import requests
import unittest
import json
import sys
import time
import concurrent.futures
from datetime import datetime

class ZamaDiceAPITester:
    def __init__(self, base_url="https://01e1466d-b420-4c40-938e-50030a4deb08.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.game_id = None
        self.wallet_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"  # Test wallet address

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "/api/health",
            200
        )
        if success:
            print(f"Health Status: {response.get('status')}")
            print(f"Service: {response.get('service')}")
        return success

    def test_play_game(self, with_wallet=False):
        """Test playing a game"""
        data = {"num_dice": 2}
        if with_wallet:
            data["player_address"] = self.wallet_address
            test_name = "Play Game with Wallet"
        else:
            test_name = "Play Game without Wallet"
            
        success, response = self.run_test(
            test_name,
            "POST",
            "/api/play",
            200,
            data=data
        )
        
        if success:
            self.game_id = response.get('game_id')
            print(f"Game ID: {self.game_id}")
            print(f"Dice Results: {response.get('dice_results')}")
            print(f"Total Score: {response.get('total_score')}")
            print(f"NFT Generated: {response.get('nft_generated')}")
            if response.get('nft_metadata'):
                print(f"NFT Name: {response.get('nft_metadata').get('name')}")
        
        return success

    def test_get_games(self):
        """Test getting game history"""
        success, response = self.run_test(
            "Get Games History",
            "GET",
            "/api/games",
            200,
            params={"limit": 5}
        )
        
        if success and 'games' in response:
            print(f"Retrieved {len(response['games'])} games")
            if len(response['games']) > 0:
                print(f"First game dice results: {response['games'][0].get('dice_results')}")
        
        return success

    def test_get_game_by_id(self):
        """Test getting a specific game by ID"""
        if not self.game_id:
            print("❌ No game ID available to test")
            return False
            
        success, response = self.run_test(
            "Get Game by ID",
            "GET",
            f"/api/game/{self.game_id}",
            200
        )
        
        if success:
            print(f"Retrieved game with ID: {response.get('id')}")
            print(f"Dice Results: {response.get('dice_results')}")
        
        return success

    def test_stats(self):
        """Test getting game statistics"""
        success, response = self.run_test(
            "Get Game Statistics",
            "GET",
            "/api/stats",
            200
        )
        
        if success:
            print(f"Total Games: {response.get('total_games')}")
            print(f"Total Users: {response.get('total_users')}")
            print(f"Total NFTs: {response.get('total_nfts')}")
            print(f"Network: {response.get('network')}")
        
        return success

    def test_create_user(self):
        """Test creating a user"""
        username = f"TestUser_{datetime.now().strftime('%H%M%S')}"
        params = {
            "wallet_address": self.wallet_address,
            "username": username
        }
            
        success, response = self.run_test(
            "Create User",
            "POST",
            f"/api/user?wallet_address={self.wallet_address}&username={username}",
            200
        )
        
        if success:
            print(f"User created/updated: {response.get('message')}")
            if 'user' in response:
                print(f"Username: {response['user'].get('username')}")
        
        return success

    def test_get_user(self):
        """Test getting a user by wallet address"""
        success, response = self.run_test(
            "Get User",
            "GET",
            f"/api/user/{self.wallet_address}",
            200
        )
        
        if success:
            print(f"Retrieved user with wallet: {response.get('wallet_address')}")
            print(f"Username: {response.get('username')}")
        
        return success

    def test_edge_cases(self):
        """Test edge cases"""
        print("\n🧪 Testing Edge Cases")
        
        # Test with invalid number of dice
        success, response = self.run_test(
            "Play with Invalid Dice Count (negative)",
            "POST",
            "/api/play",
            500,  # Expecting error
            data={"num_dice": -1}
        )
        
        # Test with large number of dice
        success, response = self.run_test(
            "Play with Large Dice Count",
            "POST",
            "/api/play",
            200,
            data={"num_dice": 10}
        )
        
        if success:
            print(f"Successfully handled large dice count: {len(response.get('dice_results'))}")
        
        # Test with invalid game ID
        success, response = self.run_test(
            "Get Game with Invalid ID",
            "GET",
            "/api/game/invalid-id-123",
            404  # Expecting not found
        )
        
        # Test with invalid wallet address
        success, response = self.run_test(
            "Get User with Invalid Wallet",
            "GET",
            "/api/user/0xinvalid-wallet-address",
            404  # Expecting not found
        )
        
        return True  # Return True as we're testing error cases
        
    def test_performance(self):
        """Test API performance"""
        print("\n⚡ Testing API Performance")
        
        # Test response time for health endpoint
        start_time = time.time()
        success, _ = self.run_test("Health Check Performance", "GET", "/api/health", 200)
        health_time = time.time() - start_time
        print(f"Health endpoint response time: {health_time:.4f} seconds")
        
        # Test response time for play endpoint
        start_time = time.time()
        success, _ = self.run_test(
            "Play Game Performance", 
            "POST", 
            "/api/play", 
            200, 
            data={"num_dice": 2}
        )
        play_time = time.time() - start_time
        print(f"Play endpoint response time: {play_time:.4f} seconds")
        
        # Test response time for games endpoint
        start_time = time.time()
        success, _ = self.run_test("Get Games Performance", "GET", "/api/games", 200)
        games_time = time.time() - start_time
        print(f"Games endpoint response time: {games_time:.4f} seconds")
        
        # Test concurrent requests
        print("\nTesting concurrent requests...")
        num_requests = 10
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self._concurrent_play_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        total_time = time.time() - start_time
        success_count = sum(1 for result in results if result)
        
        print(f"Completed {num_requests} concurrent requests in {total_time:.4f} seconds")
        print(f"Success rate: {success_count}/{num_requests} ({success_count/num_requests*100:.1f}%)")
        
        return success_count == num_requests
    
    def test_leaderboard(self):
        """Test getting the leaderboard"""
        success, response = self.run_test(
            "Get Leaderboard",
            "GET",
            "/api/leaderboard",
            200,
            params={"limit": 5}
        )
        
        if success and 'leaderboard' in response:
            print(f"Retrieved {len(response['leaderboard'])} leaderboard entries")
        
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Zama Dice API Tests")
        print("=" * 50)
        
        tests = [
            self.test_health,
            lambda: self.test_play_game(with_wallet=False),
            lambda: self.test_play_game(with_wallet=True),
            self.test_get_games,
            self.test_get_game_by_id,
            self.test_stats,
            self.test_create_user,
            self.test_get_user,
            self.test_leaderboard,
            self.test_edge_cases,
            self.test_performance
        ]
        
        for test in tests:
            test()
            print("-" * 50)
        
        print("\n📊 Test Results:")
        print(f"Tests Passed: {self.tests_passed}/{self.tests_run}")
        print("=" * 50)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = ZamaDiceAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)