"""
CLI Monitoring Dashboard for Data Pipeline.

Provides command-line interface for monitoring pipeline status,
data freshness, and system health.

Author: AI Assistant
Date: December 14, 2025
Version: 1.0
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.operations import get_latest_price, get_price_statistics
from database.models import Commodity, DataSource
from database.utils import get_session, check_database_health

logger = logging.getLogger(__name__)


class PipelineMonitor:
    """Monitor and report on pipeline status and data freshness."""
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive pipeline status.
        
        Returns:
            Dictionary with pipeline status information
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'database': self._check_database_status(),
            'data_freshness': self._check_data_freshness(),
            'commodities': self._get_commodity_list(),
            'sources': self._get_source_list()
        }
        
        return status
    
    def _check_database_status(self) -> Dict[str, Any]:
        """Check database connection and health."""
        try:
            is_healthy, message = check_database_health()
            
            return {
                'status': 'HEALTHY' if is_healthy else 'UNHEALTHY',
                'message': message,
                'accessible': True
            }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': str(e),
                'accessible': False
            }
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check how fresh the data is for each commodity/source."""
        freshness = {}
        
        try:
            with get_session() as session:
                commodities = session.query(Commodity).all()
                sources = session.query(DataSource).all()
                
                for commodity in commodities:
                    for source in sources:
                        latest = get_latest_price(commodity.symbol, source.name)
                        
                        if latest:
                            timestamp, price = latest
                            age_days = (datetime.now(timestamp.tzinfo) - timestamp).days
                            
                            key = f"{commodity.symbol}_{source.name}"
                            freshness[key] = {
                                'commodity': commodity.symbol,
                                'source': source.name,
                                'latest_date': timestamp.isoformat(),
                                'latest_price': float(price),
                                'age_days': age_days,
                                'status': 'FRESH' if age_days <= 2 else 'STALE'
                            }
        except Exception as e:
            logger.error(f"Failed to check data freshness: {e}")
        
        return freshness
    
    def _get_commodity_list(self) -> list:
        """Get list of all commodities in database."""
        try:
            with get_session() as session:
                commodities = session.query(Commodity).all()
                return [{'symbol': c.symbol, 'name': c.name} for c in commodities]
        except:
            return []
    
    def _get_source_list(self) -> list:
        """Get list of all data sources in database."""
        try:
            with get_session() as session:
                sources = session.query(DataSource).all()
                return [{'name': s.name, 'description': s.description} for s in sources]
        except:
            return []
    
    def print_status(self):
        """Print formatted status to console."""
        status = self.get_status()
        
        print("="*80)
        print(" "*25 + "PIPELINE STATUS DASHBOARD")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Database Status
        print("DATABASE STATUS:")
        db_status = status['database']
        print(f"  Status: {db_status['status']}")
        print(f"  Accessible: {db_status['accessible']}")
        if db_status.get('message'):
            print(f"  Message: {db_status['message']}")
        print()
        
        # Data Freshness
        print("DATA FRESHNESS:")
        freshness = status['data_freshness']
        
        if not freshness:
            print("  No data available")
        else:
            for key, info in freshness.items():
                status_icon = "OK" if info['status'] == 'FRESH' else "STALE"
                print(f"  [{status_icon}] {info['commodity']} ({info['source']}): "
                      f"{info['age_days']} days old, ${info['latest_price']:.2f}")
        print()
        
        # Commodities
        print("COMMODITIES:")
        for commodity in status['commodities']:
            print(f"  - {commodity['symbol']}: {commodity['name']}")
        print()
        
        # Sources
        print("DATA SOURCES:")
        for source in status['sources']:
            desc = source['description'] or 'No description'
            print(f"  - {source['name']}: {desc}")
        print()
        
        print("="*80)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Data Pipeline Monitoring Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m data_pipeline.monitor status    Show pipeline status
  python -m data_pipeline.monitor fresh     Check data freshness
        """
    )
    
    parser.add_argument(
        'command',
        choices=['status', 'fresh'],
        help='Monitoring command'
    )
    
    args = parser.parse_args()
    
    monitor = PipelineMonitor()
    
    if args.command == 'status':
        monitor.print_status()
    elif args.command == 'fresh':
        status = monitor.get_status()
        print("Data Freshness Report:")
        print("="*80)
        for key, info in status['data_freshness'].items():
            print(f"{info['commodity']} ({info['source']}): {info['age_days']} days old")


if __name__ == '__main__':
    main()

