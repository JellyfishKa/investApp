"""
LSTM Model for Stock Price Prediction
"""
import numpy as np
from typing import Optional, Tuple
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from loguru import logger
import joblib


class LSTMStockModel:
    """
    LSTM-based model for stock price prediction
    
    Architecture:
    - Input: (sequence_length, num_features)
    - LSTM layer 1: 128 units, return_sequences=True
    - Dropout: 0.2
    - LSTM layer 2: 64 units
    - Dropout: 0.2
    - Dense: 32 units, ReLU activation
    - Output: 1 unit (predicted price)
    """
    
    def __init__(
        self,
        ticker: str,
        sequence_length: int = 60,
        num_features: int = 17  # Number of features from preprocessor
    ):
        self.ticker = ticker
        self.sequence_length = sequence_length
        self.num_features = num_features
        self.model: Optional[keras.Model] = None
        self.history = None
    
    def build_model(self) -> keras.Model:
        """
        Build LSTM model architecture
        
        Returns:
            Compiled Keras model
        """
        model = keras.Sequential([
            # First LSTM layer
            layers.LSTM(
                128,
                return_sequences=True,
                input_shape=(self.sequence_length, self.num_features),
                name='lstm_1'
            ),
            layers.Dropout(0.2, name='dropout_1'),
            
            # Second LSTM layer
            layers.LSTM(64, return_sequences=False, name='lstm_2'),
            layers.Dropout(0.2, name='dropout_2'),
            
            # Dense layers
            layers.Dense(32, activation='relu', name='dense_1'),
            layers.Dropout(0.1, name='dropout_3'),
            
            # Output layer
            layers.Dense(1, name='output')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='huber',  # Huber loss is robust to outliers
            metrics=['mae', 'mse']
        )
        
        self.model = model
        logger.info(f"Model built for {self.ticker}")
        logger.info(f"Total parameters: {model.count_params():,}")
        
        return model
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32
    ) -> keras.callbacks.History:
        """
        Train the model
        
        Args:
            X_train: Training sequences (samples, sequence_length, features)
            y_train: Training targets (samples,)
            X_val: Validation sequences
            y_val: Validation targets
            epochs: Number of epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                filepath=f'models/{self.ticker}_best.keras',
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]
        
        logger.info(f"Training {self.ticker} model...")
        logger.info(f"Train samples: {len(X_train)}, Val samples: {len(X_val)}")
        
        # Train
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info(f"Training completed for {self.ticker}")
        return self.history
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Input sequences (samples, sequence_length, features)
            
        Returns:
            Predictions (samples,)
        """
        if self.model is None:
            raise ValueError("Model not built or loaded")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def predict_single(self, sequence: np.ndarray) -> float:
        """
        Predict price for a single sequence
        
        Args:
            sequence: Single sequence (sequence_length, features)
            
        Returns:
            Predicted price (scaled)
        """
        if self.model is None:
            raise ValueError("Model not built or loaded")
        
        # Reshape for batch prediction
        X = sequence.reshape(1, self.sequence_length, self.num_features)
        prediction = self.model.predict(X, verbose=0)
        
        return float(prediction[0, 0])
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> dict:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test sequences
            y_test: Test targets
            
        Returns:
            Dictionary with metrics
        """
        if self.model is None:
            raise ValueError("Model not built or loaded")
        
        # Get predictions
        y_pred = self.predict(X_test)
        
        # Calculate metrics
        mae = np.mean(np.abs(y_test - y_pred))
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        
        # MAPE (Mean Absolute Percentage Error)
        # Avoid division by zero
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100
        
        # R² Score
        ss_res = np.sum((y_test - y_pred) ** 2)
        ss_tot = np.sum((y_test - np.mean(y_test)) ** 2)
        r2 = 1 - (ss_res / ss_tot)
        
        metrics = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2': float(r2),
            'test_samples': len(X_test)
        }
        
        logger.info(f"Model evaluation for {self.ticker}:")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        logger.info(f"  R²: {r2:.4f}")
        
        return metrics
    
    def save(self, directory: str = "models"):
        """
        Save model to disk
        
        Args:
            directory: Directory to save model
        """
        if self.model is None:
            raise ValueError("No model to save")
        
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Save Keras model
        model_path = Path(directory) / f"{self.ticker}_model.keras"
        self.model.save(model_path)
        
        # Save training history
        if self.history:
            history_path = Path(directory) / f"{self.ticker}_history.pkl"
            joblib.dump(self.history.history, history_path)
        
        logger.info(f"Model saved to {model_path}")
    
    def load(self, directory: str = "models"):
        """
        Load model from disk
        
        Args:
            directory: Directory containing model
        """
        model_path = Path(directory) / f"{self.ticker}_model.keras"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.model = keras.models.load_model(model_path)
        logger.info(f"Model loaded from {model_path}")
        
        # Try to load history
        history_path = Path(directory) / f"{self.ticker}_history.pkl"
        if history_path.exists():
            history_dict = joblib.load(history_path)
            logger.info(f"Training history loaded")
    
    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        if self.model is None:
            return "Model not built"
        
        import io
        stream = io.StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        return stream.getvalue()
