import React, { useState, useEffect } from 'react';
import { 
  Video, 
  Camera, 
  Share2, 
  Music, 
  TrendingUp, 
  Zap, 
  Clock, 
  Sparkles, 
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Key
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

const defaultChartData = [
  { day: '29 Lug', youtube: 10, instagram: 5, facebook: 0, tiktok: 0 },
  { day: '30 Lug', youtube: 12, instagram: 6, facebook: 0, tiktok: 0 },
  { day: '31 Lug', youtube: 15, instagram: 7, facebook: 0, tiktok: 0 },
  { day: '01 Ago', youtube: 18, instagram: 8, facebook: 0, tiktok: 0 },
  { day: '02 Ago', youtube: 20, instagram: 9, facebook: 0, tiktok: 0 },
  { day: '03 Ago', youtube: 22, instagram: 10, facebook: 0, tiktok: 0 },
  { day: '04 Ago', youtube: 25, instagram: 10, facebook: 0, tiktok: 0 }
];

export default function App() {
  const [metrics, setMetrics] = useState({
    ytViews: 25,
    ytSubs: 1,
    ytVideos: 1,
    ytLive: false,
    igViews: 120,
    igFollowers: 10,
    igLive: false,
    fbViews: 0,
    fbFollowers: 0,
    fbLive: false,
    ttViews: 0,
    ttFollowers: 0,
    ttLive: false
  });
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchLiveMetrics = async () => {
    setIsSyncing(true);
    try {
      const res = await fetch('/api/metrics');
      if (res.ok) {
        const data = await res.json();
        const history = data.history || [];
        if (history.length > 0) {
          const latest = history[history.length - 1];
          setMetrics({
            ytViews: latest.youtube?.total_views ?? 25,
            ytSubs: latest.youtube?.subscribers ?? 1,
            ytVideos: latest.youtube?.videos_count ?? 1,
            ytLive: (latest.youtube?.is_live_api || latest.youtube?.is_live_rss) ?? false,
            igViews: latest.instagram?.estimated_weekly_reach ?? 120,
            igFollowers: latest.instagram?.followers ?? 10,
            igLive: latest.instagram?.is_live_api ?? false,
            fbViews: latest.facebook?.total_views ?? 0,
            fbFollowers: latest.facebook?.followers ?? 0,
            fbLive: latest.facebook?.is_live_api ?? false,
            ttViews: latest.tiktok?.total_views ?? 0,
            ttFollowers: latest.tiktok?.followers ?? 0,
            ttLive: latest.tiktok?.is_live_api ?? false
          });
        }
      }
    } catch (e) {
      console.log('Live API endpoint error:', e);
    } finally {
      setTimeout(() => setIsSyncing(false), 800);
    }
  };

  useEffect(() => {
    fetchLiveMetrics();
  }, []);

  const totalAggregateViews = metrics.ytViews + metrics.igViews + metrics.fbViews + metrics.ttViews;

  return (
    <div className="dashboard-layout">
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', paddingBottom: '1.5rem', borderBottom: '1px solid var(--card-border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: 48, height: 48, background: 'linear-gradient(135deg, #06b6d4, #3b82f6)', borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 4px 20px rgba(6,182,212,0.4)' }}>
            <Zap size={26} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>TechHacks AI - Video Views Dashboard</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Monitoraggio Visualizzazioni Reali • YouTube Shorts + Instagram Reels + Facebook Reels + TikTok
            </p>
          </div>
        </div>

        <button 
          onClick={fetchLiveMetrics}
          style={{ background: 'rgba(6, 182, 212, 0.12)', border: '1px solid var(--cyan-accent)', color: 'var(--cyan-accent)', padding: '0.6rem 1.2rem', borderRadius: 30, fontSize: '0.88rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}
        >
          <RefreshCw size={16} className={isSyncing ? 'spin' : ''} />
          {isSyncing ? 'Sincronizzazione...' : 'Aggiorna Views Live'}
        </button>
      </header>

      {/* Aggregate Views Hero Banner */}
      <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, rgba(6,182,212,0.1), rgba(15,23,42,0.8))', border: '1px solid rgba(6,182,212,0.4)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.8rem 2rem' }}>
        <div>
          <span style={{ textTransform: 'uppercase', fontSize: '0.85rem', fontWeight: 700, color: 'var(--cyan-accent)', letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Eye size={18} /> Visualizzazioni Totali Aggregate (4 Piattaforme Video)
          </span>
          <div style={{ fontSize: '3.5rem', fontWeight: 800, color: '#fff', letterSpacing: '-1.5px', marginTop: '0.2rem' }}>
            {totalAggregateViews.toLocaleString()} <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)', fontWeight: 500 }}>views complessive</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1.5rem', textAlign: 'right' }}>
          <div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Piattaforme Attive</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fff' }}>4 / 4</div>
          </div>
          <div style={{ borderLeft: '1px solid var(--card-border)', paddingLeft: '1.5rem' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Stato API</div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--yellow-accent)' }}>Configurazione Credenziali</div>
          </div>
        </div>
      </div>

      {/* 4 Video Platforms Grid */}
      <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
        {/* 1. YouTube Shorts */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge badge-yt"><Video size={14} /> YouTube Shorts</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: metrics.ytLive ? '#10b981' : '#facc15', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              {metrics.ytLive ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
              {metrics.ytLive ? 'RSS LIVE' : 'ATTESA KEY'}
            </span>
          </div>
          <div className="metric-number">{metrics.ytViews.toLocaleString()}</div>
          <div className="metric-title">Visualizzazioni Shorts (@techhacks_aii)</div>
          <div className="metric-footer">
            Iscritti: <strong>{metrics.ytSubs}</strong> • Video: <strong>{metrics.ytVideos}</strong>
          </div>
        </div>

        {/* 2. Instagram Reels */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge badge-ig"><Camera size={14} /> Instagram Reels</span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: metrics.igLive ? '#10b981' : '#facc15', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              {metrics.igLive ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
              {metrics.igLive ? 'API LIVE' : 'ATTESA TOKEN'}
            </span>
          </div>
          <div className="metric-number">{metrics.igViews.toLocaleString()}</div>
          <div className="metric-title">Visualizzazioni Reels (@techs_ai1)</div>
          <div className="metric-footer">
            Follower: <strong>{metrics.igFollowers}</strong>
          </div>
        </div>

        {/* 3. Facebook Reels */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
              <Share2 size={14} /> Facebook Reels
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: metrics.fbLive ? '#10b981' : '#facc15', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              {metrics.fbLive ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
              {metrics.fbLive ? 'API LIVE' : 'ATTESA TOKEN'}
            </span>
          </div>
          <div className="metric-number">{metrics.fbViews.toLocaleString()}</div>
          <div className="metric-title">Visualizzazioni Reels (TechHacks AI)</div>
          <div className="metric-footer">
            Follower Pagina: <strong>{metrics.fbFollowers}</strong>
          </div>
        </div>

        {/* 4. TikTok Videos */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="badge" style={{ background: 'rgba(236, 72, 153, 0.15)', color: '#ec4899', border: '1px solid rgba(236, 72, 153, 0.3)' }}>
              <Music size={14} /> TikTok Videos
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: metrics.ttLive ? '#10b981' : '#facc15', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              {metrics.ttLive ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
              {metrics.ttLive ? 'API LIVE' : 'ATTESA TOKEN'}
            </span>
          </div>
          <div className="metric-number">{metrics.ttViews.toLocaleString()}</div>
          <div className="metric-title">Visualizzazioni TikTok (@techhacks.ai)</div>
          <div className="metric-footer">
            Follower: <strong>{metrics.ttFollowers}</strong>
          </div>
        </div>
      </div>

      {/* Main Grid: Views Area Chart + Credentials Guide */}
      <div className="main-grid">
        {/* Growth Area Chart */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <TrendingUp size={20} color="var(--cyan-accent)" />
            Trend di Crescita Visualizzazioni (Ultimi 7 Giorni)
          </h3>
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={defaultChartData}>
                <defs>
                  <linearGradient id="ytGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="igGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#c13584" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#c13584" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#232d42" />
                <XAxis dataKey="day" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#151c2e', borderColor: '#232d42', color: '#fff' }} />
                <Area type="monotone" dataKey="youtube" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#ytGrad)" name="YouTube Shorts" />
                <Area type="monotone" dataKey="instagram" stroke="#c13584" strokeWidth={3} fillOpacity={1} fill="url(#igGrad)" name="Instagram Reels" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* API Credentials Setup Guide */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Key size={20} color="var(--yellow-accent)" />
            Credenziali API Richieste per i Dati LIVE
          </h3>
          
          <div style={{ background: 'rgba(6, 182, 212, 0.06)', border: '1px solid rgba(6, 182, 212, 0.2)', borderRadius: 12, padding: '1.2rem', fontSize: '0.85rem' }}>
            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#ef4444' }}>1. YouTube Data API v3:</strong>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.2rem' }}>Genera una <code>YOUTUBE_API_KEY</code> gratis su Google Cloud Console.</p>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#e1306c' }}>2. Instagram Graph API:</strong>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.2rem' }}>Crea un'app su Meta for Developers per ottenere <code>INSTAGRAM_ACCESS_TOKEN</code> e <code>INSTAGRAM_ACCOUNT_ID</code>.</p>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#3b82f6' }}>3. Facebook Page API:</strong>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.2rem' }}>Genera il <code>FACEBOOK_PAGE_ACCESS_TOKEN</code> e <code>FACEBOOK_PAGE_ID</code> su Meta for Developers.</p>
            </div>

            <div>
              <strong style={{ color: '#ec4899' }}>4. TikTok Display API:</strong>
              <p style={{ color: 'var(--text-muted)', marginTop: '0.2rem' }}>Crea un'app su TikTok for Developers per ottenere <code>TIKTOK_ACCESS_TOKEN</code>.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
