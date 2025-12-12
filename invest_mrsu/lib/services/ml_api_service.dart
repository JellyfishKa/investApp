import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/prediction.dart';

/// Service for interacting with ML Backend API
class MLApiService {
  // TODO: Replace with your actual backend URL
  // For local development: 'http://localhost:8000'
  // For production: 'https://your-backend.onrender.com'
  static const String baseUrl = 'http://localhost:8000';

  final http.Client _client;

  MLApiService({http.Client? client}) : _client = client ?? http.Client();

  /// Get predictions for a stock ticker
  ///
  /// Fetches predictions for all three periods (week, month, year)
  /// and returns a PredictionSet
  Future<PredictionSet> getPredictions(String ticker) async {
    try {
      // Fetch predictions in parallel
      final results = await Future.wait([
        _fetchPrediction(ticker, 'week'),
        _fetchPrediction(ticker, 'month'),
        _fetchPrediction(ticker, 'year'),
      ]);

      return PredictionSet(
        ticker: ticker,
        weekPrediction: results[0],
        monthPrediction: results[1],
        yearPrediction: results[2],
      );
    } catch (e) {
      print('Error getting predictions for $ticker: $e');
      rethrow;
    }
  }

  /// Fetch single prediction from API
  Future<Prediction?> _fetchPrediction(String ticker, String period) async {
    try {
      final response = await _client
          .post(
            Uri.parse('$baseUrl/predict'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'ticker': ticker, 'period': period}),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return _parsePrediction(data, period);
      } else if (response.statusCode == 404) {
        print('Model not found for $ticker');
        return null;
      } else {
        print('API error: ${response.statusCode} - ${response.body}');
        return null;
      }
    } catch (e) {
      print('Network error fetching $period prediction for $ticker: $e');
      return null;
    }
  }

  /// Parse prediction response into Prediction object
  Prediction _parsePrediction(Map<String, dynamic> data, String period) {
    return Prediction(
      ticker: data['ticker'],
      targetDate: DateTime.parse(data['prediction_date']),
      predictedPrice: data['predicted_price'].toDouble(),
      confidenceLow: data['confidence_low']?.toDouble() ?? 0.0,
      confidenceHigh: data['confidence_high']?.toDouble() ?? 0.0,
      changePercent: data['change_percent'].toDouble(),
      period: period,
    );
  }

  /// Get historical price data
  Future<List<Map<String, dynamic>>> getHistory(
    String ticker, {
    int days = 365,
  }) async {
    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/history/$ticker?days=$days'))
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return List<Map<String, dynamic>>.from(data['data']);
      } else {
        print('API error: ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('Error fetching history for $ticker: $e');
      return [];
    }
  }

  /// Check if API is healthy
  Future<bool> checkHealth() async {
    try {
      final response = await _client
          .get(Uri.parse('$baseUrl/'))
          .timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      print('Health check failed: $e');
      return false;
    }
  }

  /// Dispose HTTP client
  void dispose() {
    _client.close();
  }
}
