import { useState, useEffect } from 'react';
import { Activity, Filter, Clock, Search } from 'lucide-react';
import useWatcher from '../hooks/useWatcher';

export default function ActivityLog() {
  const { events: liveEvents } = useWatcher();
  const [filter, setFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [historyEvents, setHistoryEvents] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/activity')
      .then(res => res.json())
      .then(data => {
        if (data && data.events) {
          setHistoryEvents(data.events);
        }
      })
      .catch(e => console.error("Error fetching activity log:", e));
  }, []);

  // Merge history with live events, avoiding duplicates by watch_id/timestamp
  const mergedEvents = [...liveEvents];
  for (const he of historyEvents) {
    if (!mergedEvents.find(le => le.timestamp === he.timestamp && le.watch_id === he.watch_id)) {
      mergedEvents.push(he);
    }
  }

  // Sort by timestamp descending
  mergedEvents.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  const filteredEvents = mergedEvents.filter(ev => {
    if (filter !== 'all' && (ev.connector || '').toLowerCase() !== filter.toLowerCase()) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchSummary = (ev.summary || '').toLowerCase().includes(q);
      const matchType = (ev.event_type || '').toLowerCase().includes(q);
      if (!matchSummary && !matchType) return false;
    }
    return true;
  });

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-1">Activity & Audit Log</h1>
          <p className="text-sm text-gray-400">
            Real-time event stream captured by the Lear Watcher across all monitored services.
          </p>
        </div>

      <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
          <input
            type="text"
            placeholder="Search events, errors, keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface border border-border-subtle rounded-xl pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:border-accent outline-none transition-colors"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
          <span className="text-xs text-gray-500 font-mono flex items-center gap-1">
            <Filter size={12} /> Filter:
          </span>
          {['all', 'aws', 'github', 'datadog'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition-all cursor-pointer ${
                filter === f
                  ? 'bg-accent text-gray-950 shadow'
                  : 'bg-surface text-gray-400 hover:text-white border border-border-subtle'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      </div>

      <div className="glass-panel rounded-2xl p-6 border border-border-subtle shadow-xl">
        {filteredEvents.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center text-gray-500">
            <Clock size={32} className="mb-2 text-gray-600" />
            <span className="text-sm font-medium">No activity events recorded yet</span>
            <span className="text-xs text-gray-600 mt-1">Start watching a service to stream events in real time.</span>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredEvents.map((ev, i) => (
              <div
                key={i}
                className="flex items-start justify-between p-4 rounded-xl bg-surface/50 border border-border-subtle hover:border-border-hover transition-colors"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-surface-elevated border border-border-subtle text-accent mt-0.5">
                    <Activity size={16} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-white">{ev.summary || ev.event_type}</span>
                      {ev.connector && (
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-accent/15 text-accent">
                          {ev.connector}
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-gray-400 font-mono mt-1">
                      Event Type: {ev.event_type}
                    </p>
                  </div>
                </div>

                <span className="text-[11px] text-gray-500 font-mono shrink-0">
                  {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
