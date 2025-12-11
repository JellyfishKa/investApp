"""
ML Model Training Pipeline
Orchestrates data loading, preprocessing, and model training
"""
import asyncio
from typing import List, Optional
from pathlib import Path
from loguru import logger
from database.db import async_session_maker, init_db
from ml.preprocessor import DataPreprocessor
from ml.model import LSTMStockModel
import json
from datetime import datetime


class ModelTrainer:
    """Orchestrator for training ML models"""
    
    TICKERS = ['GAZP', 'GAZP-p', 'SIBN', 'GCHE', 'MRKZ']
    
    def __init__(
        self,
        sequence_length: int = 60,
        target_days: int = 30,
        epochs: int = 100,
        batch_size: int = 32
    ):
        self.sequence_length = sequence_length
        self.target_days = target_days
        self.epochs = epochs
        self.batch_size = batch_size
        self.results = {}
    
    async def train_ticker(self, ticker: str) -> dict:
        """
        Train model for a single ticker
        
        Args:
            ticker: Stock ticker
            
        Returns:
            Training results and metrics
        """
        logger.info(f"{'='*60}")
        logger.info(f"Training model for {ticker}")
        logger.info(f"{'='*60}")
        
        try:
            # Initialize preprocessor
            preprocessor = DataPreprocessor(ticker)
            
            # Load data from database
            async with async_session_maker() as db:
                df = await preprocessor.load_data(db)
            
            logger.info(f"Loaded {len(df)} records")
            
            # Create technical indicators
            df = preprocessor.create_technical_indicators(df)
            
            # Prepare sequences
            X, y = preprocessor.prepare_sequences(
                df,
                sequence_length=self.sequence_length,
                target_days=self.target_days
            )
            
            # Split data
            X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split_data(X, y)
            
            # Initialize model
            model = LSTMStockModel(
                ticker=ticker,
                sequence_length=self.sequence_length,
                num_features=X_train.shape[2]
            )
            
            # Build model
            model.build_model()
            logger.info(f"\n{model.get_model_summary()}")
            
            # Train model
            history = model.train(
                X_train, y_train,
                X_val, y_val,
                epochs=self.epochs,
                batch_size=self.batch_size
            )
            
            # Evaluate on test set
            metrics = model.evaluate(X_test, y_test)
            
            # Save model
            model.save()
            
            # Save preprocessor (for later use in prediction)
            import joblib
            Path("models").mkdir(exist_ok=True)
            joblib.dump(preprocessor, f"models/{ticker}_preprocessor.pkl")
            
            result = {
                'ticker': ticker,
                'status': 'success',
                'metrics': metrics,
                'train_samples': len(X_train),
                'val_samples': len(X_val),
                'test_samples': len(X_test),
                'sequence_length': self.sequence_length,
                'target_days': self.target_days,
                'trained_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Successfully trained {ticker}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to train {ticker}: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'ticker': ticker,
                'status': 'failed',
                'error': str(e),
                'trained_at': datetime.now().isoformat()
            }
    
    async def train_all(self, tickers: Optional[List[str]] = None):
        """
        Train models for all tickers
        
        Args:
            tickers: List of tickers to train (default: all)
        """
        if tickers is None:
            tickers = self.TICKERS
        
        logger.info(f"Starting training for {len(tickers)} tickers")
        logger.info(f"Configuration:")
        logger.info(f"  Sequence Length: {self.sequence_length}")
        logger.info(f"  Target Days: {self.target_days}")
        logger.info(f"  Epochs: {self.epochs}")
        logger.info(f"  Batch Size: {self.batch_size}")
        
        # Train each ticker
        for ticker in tickers:
            result = await self.train_ticker(ticker)
            self.results[ticker] = result
        
        # Save training summary
        self._save_summary()
        
        logger.info(f"\n{'='*60}")
        logger.info("Training Summary")
        logger.info(f"{'='*60}")
        
        successful = sum(1 for r in self.results.values() if r['status'] == 'success')
        failed = len(self.results) - successful
        
        logger.info(f"Total: {len(self.results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")
        
        for ticker, result in self.results.items():
            if result['status'] == 'success':
                metrics = result['metrics']
                logger.info(f"\n{ticker}:")
                logger.info(f"  MAPE: {metrics['mape']:.2f}%")
                logger.info(f"  RMSE: {metrics['rmse']:.4f}")
                logger.info(f"  R²: {metrics['r2']:.4f}")
    
    def _save_summary(self):
        """Save training summary to JSON"""
        summary_path = Path("models") / "training_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Training summary saved to {summary_path}")


async def main():
    """Main training function"""
    # Initialize database
    await init_db()
    
    # Create trainer
    trainer = ModelTrainer(
        sequence_length=60,  # 60 days of history
        target_days=30,      # Predict 30 days ahead (month)
        epochs=100,
        batch_size=32
    )
    
    # Train all models
    await trainer.train_all()
    
    logger.info("\n🎉 Training completed!")


if __name__ == "__main__":
    # Configure logging
    logger.add("logs/training_{time}.log", rotation="1 day")
    
    # Run training
    asyncio.run(main())
