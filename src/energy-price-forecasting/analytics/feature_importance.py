"""
Feature Importance Analysis using SHAP.

Analyzes feature importance for ML models using SHAP (SHapley Additive exPlanations)
values to explain model predictions.

Author: AI Assistant
Date: December 15, 2025
Version: 1.0
"""

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    shap = None

logger = logging.getLogger(__name__)


class FeatureImportanceAnalyzer:
    """
    Analyzes feature importance using SHAP values.
    
    Provides methods to calculate SHAP values and visualize feature
    importance for ML models.
    """
    
    def __init__(self):
        """Initialize FeatureImportanceAnalyzer."""
        if not SHAP_AVAILABLE:
            logger.warning("SHAP library not available - feature importance analysis will be limited")
        logger.info("FeatureImportanceAnalyzer initialized")
    
    def calculate_shap_values(
        self,
        model: any,
        X: pd.DataFrame,
        model_type: str = 'tree'
    ) -> Optional[Tuple[np.ndarray, any]]:
        """
        Calculate SHAP values for a model.
        
        Args:
            model: Trained ML model
            X: Feature DataFrame
            model_type: Type of model ('tree', 'linear', 'neural', 'auto')
            
        Returns:
            Tuple of (SHAP values, explainer) or None
        """
        if not SHAP_AVAILABLE:
            logger.error("SHAP library required for SHAP value calculation")
            return None
        
        logger.info(f"Calculating SHAP values (model_type={model_type})...")
        
        try:
            # Create explainer based on model type
            if model_type == 'tree' or model_type == 'auto':
                # Tree-based models (XGBoost, LightGBM, Random Forest)
                try:
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(X)
                except:
                    # Fallback to KernelExplainer
                    explainer = shap.KernelExplainer(model.predict, X.sample(min(100, len(X))))
                    shap_values = explainer.shap_values(X.sample(min(1000, len(X))))
            
            elif model_type == 'linear':
                explainer = shap.LinearExplainer(model, X)
                shap_values = explainer.shap_values(X)
            
            elif model_type == 'neural':
                explainer = shap.DeepExplainer(model, X.values)
                shap_values = explainer.shap_values(X.values)
            
            else:
                # Generic KernelExplainer
                explainer = shap.KernelExplainer(model.predict, X.sample(min(100, len(X))))
                shap_values = explainer.shap_values(X.sample(min(1000, len(X))))
            
            logger.info("SHAP values calculated successfully")
            return shap_values, explainer
            
        except Exception as e:
            logger.error(f"Failed to calculate SHAP values: {e}", exc_info=True)
            return None
    
    def get_feature_importance(
        self,
        shap_values: np.ndarray,
        feature_names: List[str]
    ) -> pd.DataFrame:
        """
        Get feature importance from SHAP values.
        
        Args:
            shap_values: SHAP values array
            feature_names: List of feature names
            
        Returns:
            DataFrame with feature importance
        """
        # Handle multi-output models
        if len(shap_values.shape) > 2:
            # Average across outputs
            shap_values = np.mean(np.abs(shap_values), axis=0)
        
        # Calculate mean absolute SHAP values
        if len(shap_values.shape) == 2:
            importance = np.abs(shap_values).mean(axis=0)
        else:
            importance = np.abs(shap_values)
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names[:len(importance)],
            'importance': importance,
            'abs_importance': np.abs(importance)
        })
        
        # Sort by importance
        importance_df = importance_df.sort_values('abs_importance', ascending=False)
        
        return importance_df
    
    def analyze_feature_interactions(
        self,
        shap_values: np.ndarray,
        feature_names: List[str],
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Analyze feature interactions using SHAP interaction values.
        
        Args:
            shap_values: SHAP values
            feature_names: List of feature names
            top_n: Number of top interactions to return
            
        Returns:
            DataFrame with interaction strengths
        """
        logger.info("Analyzing feature interactions...")
        
        # Calculate interaction matrix (simplified)
        # In production, would use SHAP interaction values
        
        if len(shap_values.shape) != 2:
            logger.warning("SHAP values must be 2D for interaction analysis")
            return pd.DataFrame()
        
        n_features = shap_values.shape[1]
        interactions = []
        
        for i in range(n_features):
            for j in range(i+1, n_features):
                # Calculate correlation of SHAP values as proxy for interaction
                interaction_strength = np.corrcoef(
                    shap_values[:, i],
                    shap_values[:, j]
                )[0, 1]
                
                if not np.isnan(interaction_strength):
                    interactions.append({
                        'feature1': feature_names[i],
                        'feature2': feature_names[j],
                        'interaction_strength': abs(interaction_strength)
                    })
        
        if interactions:
            df = pd.DataFrame(interactions)
            df = df.sort_values('interaction_strength', ascending=False)
            return df.head(top_n)
        else:
            return pd.DataFrame()
    
    def explain_prediction(
        self,
        explainer: any,
        instance: pd.Series,
        feature_names: List[str]
    ) -> Dict[str, any]:
        """
        Explain a single prediction.
        
        Args:
            explainer: SHAP explainer
            instance: Single instance to explain
            feature_names: List of feature names
            
        Returns:
            Dictionary with explanation
        """
        try:
            shap_values = explainer.shap_values(instance)
            
            # Get feature contributions
            contributions = {}
            if isinstance(shap_values, np.ndarray):
                if len(shap_values.shape) == 1:
                    for i, feature in enumerate(feature_names):
                        contributions[feature] = shap_values[i]
                else:
                    # Multi-output
                    for i, feature in enumerate(feature_names):
                        contributions[feature] = shap_values[0, i]
            
            # Sort by absolute contribution
            sorted_contributions = sorted(
                contributions.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            return {
                'contributions': dict(sorted_contributions),
                'top_features': [f[0] for f in sorted_contributions[:5]],
                'total_impact': sum(contributions.values())
            }
            
        except Exception as e:
            logger.error(f"Failed to explain prediction: {e}")
            return {
                'contributions': {},
                'error': str(e)
            }
    
    def calculate_permutation_importance(
        self,
        model: any,
        X: pd.DataFrame,
        y: pd.Series,
        metric: str = 'mse',
        n_repeats: int = 10
    ) -> pd.DataFrame:
        """
        Calculate permutation importance (fallback if SHAP unavailable).
        
        Args:
            model: Trained model
            X: Feature DataFrame
            y: Target series
            metric: Evaluation metric
            n_repeats: Number of permutation repeats
            
        Returns:
            DataFrame with permutation importance
        """
        logger.info("Calculating permutation importance...")
        
        # Get baseline score
        if hasattr(model, 'predict'):
            baseline_pred = model.predict(X)
        else:
            baseline_pred = model(X)
        
        if metric == 'mse':
            baseline_score = np.mean((baseline_pred - y) ** 2)
        else:
            baseline_score = np.mean(np.abs(baseline_pred - y))
        
        importance_scores = []
        
        for feature in X.columns:
            scores = []
            X_permuted = X.copy()
            
            for _ in range(n_repeats):
                # Permute feature
                X_permuted[feature] = np.random.permutation(X_permuted[feature])
                
                # Predict
                if hasattr(model, 'predict'):
                    pred = model.predict(X_permuted)
                else:
                    pred = model(X_permuted)
                
                # Calculate score
                if metric == 'mse':
                    score = np.mean((pred - y) ** 2)
                else:
                    score = np.mean(np.abs(pred - y))
                
                scores.append(score)
            
            # Importance = increase in error
            importance = np.mean(scores) - baseline_score
            importance_scores.append({
                'feature': feature,
                'importance': importance,
                'abs_importance': abs(importance)
            })
        
        df = pd.DataFrame(importance_scores)
        df = df.sort_values('abs_importance', ascending=False)
        
        return df

