import boto3
import socket
import os
from botocore.exceptions import ClientError

class HighScoreManager:
    def __init__(self, table_name='AsteroidsHighScores', region='us-east-2'):
        """Initialize the high score manager with AWS DynamoDB."""
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table_name = table_name
        self.table = self.dynamodb.Table(table_name)
        self.player_id = self._get_player_id()
        self.high_score = 0
        self.load_high_score()
    
    def _get_player_id(self):
        """Generate a unique player ID based on hostname and username."""
        hostname = socket.gethostname()
        username = os.environ.get('USER', 'player')
        return f"{username}@{hostname}"
    
    def load_high_score(self):
        """Load the high score from DynamoDB."""
        try:
            response = self.table.get_item(
                Key={'player_id': self.player_id}
            )
            if 'Item' in response:
                self.high_score = response['Item'].get('high_score', 0)
                print(f"Loaded high score: {self.high_score}")
            else:
                print("No high score found, starting with 0")
        except ClientError as e:
            print(f"Error loading high score: {e}")
            # If there's an error, we'll just use 0 as the high score
    
    def update_high_score(self, score):
        """Update the high score if the new score is higher."""
        if score > self.high_score:
            self.high_score = score
            try:
                self.table.put_item(
                    Item={
                        'player_id': self.player_id,
                        'high_score': score
                    }
                )
                print(f"New high score saved: {score}")
                return True
            except ClientError as e:
                print(f"Error saving high score: {e}")
                return False
        return False
    
    def get_high_score(self):
        """Get the current high score."""
        return self.high_score
