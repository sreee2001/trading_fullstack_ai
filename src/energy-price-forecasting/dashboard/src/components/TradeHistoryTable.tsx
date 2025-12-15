/**
 * Trade History Table Component
 * 
 * Displays a table of trades with entry/exit details and P&L.
 */

import React, { useState, useMemo } from 'react';
import type { Trade } from '../types/api';
import { format } from 'date-fns';
import './TradeHistoryTable.css';

interface TradeHistoryTableProps {
  trades: Trade[];
}

type SortField = 'entry_date' | 'exit_date' | 'pnl' | 'position';
type SortDirection = 'asc' | 'desc';

const TradeHistoryTable: React.FC<TradeHistoryTableProps> = ({ trades }) => {
  const [sortField, setSortField] = useState<SortField>('entry_date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const sortedTrades = useMemo(() => {
    const sorted = [...trades].sort((a, b) => {
      let aValue: number | string = 0;
      let bValue: number | string = 0;

      switch (sortField) {
        case 'entry_date':
        case 'exit_date':
          aValue = new Date(a[sortField]).getTime();
          bValue = new Date(b[sortField]).getTime();
          break;
        case 'pnl':
          aValue = a.pnl;
          bValue = b.pnl;
          break;
        case 'position':
          aValue = a.position;
          bValue = b.position;
          break;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc'
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });

    return sorted;
  }, [trades, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '↕';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  const totalPnL = trades.reduce((sum, trade) => sum + trade.pnl, 0);
  const winningTrades = trades.filter((t) => t.pnl > 0).length;
  const losingTrades = trades.filter((t) => t.pnl < 0).length;

  return (
    <div className="trade-history-table">
      <div className="table-header">
        <h3>Trade History</h3>
        <div className="trade-stats">
          <span className="stat-item">
            Total Trades: <strong>{trades.length}</strong>
          </span>
          <span className="stat-item">
            Winning: <strong className="positive">{winningTrades}</strong>
          </span>
          <span className="stat-item">
            Losing: <strong className="negative">{losingTrades}</strong>
          </span>
          <span className="stat-item">
            Total P&L:{' '}
            <strong className={totalPnL >= 0 ? 'positive' : 'negative'}>
              ${totalPnL.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </strong>
          </span>
        </div>
      </div>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th onClick={() => handleSort('entry_date')} className="sortable">
                Entry Date {getSortIcon('entry_date')}
              </th>
              <th onClick={() => handleSort('exit_date')} className="sortable">
                Exit Date {getSortIcon('exit_date')}
              </th>
              <th onClick={() => handleSort('position')} className="sortable">
                Position {getSortIcon('position')}
              </th>
              <th>Entry Price</th>
              <th>Exit Price</th>
              <th onClick={() => handleSort('pnl')} className="sortable">
                P&L {getSortIcon('pnl')}
              </th>
              <th>Capital After</th>
            </tr>
          </thead>
          <tbody>
            {sortedTrades.map((trade, index) => (
              <tr key={index} className={trade.pnl >= 0 ? 'winning-trade' : 'losing-trade'}>
                <td>{format(new Date(trade.entry_date), 'MMM dd, yyyy')}</td>
                <td>{format(new Date(trade.exit_date), 'MMM dd, yyyy')}</td>
                <td>
                  <span className={`position-badge position-${trade.position}`}>
                    {trade.position.toUpperCase()}
                  </span>
                </td>
                <td>${trade.entry_price.toFixed(2)}</td>
                <td>${trade.exit_price.toFixed(2)}</td>
                <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                  ${trade.pnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </td>
                <td>${trade.capital_after_trade.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TradeHistoryTable;

