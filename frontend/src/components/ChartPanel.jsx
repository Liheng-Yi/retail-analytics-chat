import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  PieChart, Pie, Cell, Legend, ResponsiveContainer,
} from 'recharts';

const COLORS = ['#6c63ff', '#a78bfa', '#34d399', '#fbbf24', '#f87171', '#38bdf8'];

function ChartPanel({ charts }) {
  if (!charts || charts.length === 0) return null;

  return (
    <div className="chart-panel">
      {charts.map((chart, i) => (
        <div key={i} className="chart-card">
          <h4 className="chart-title">{chart.title}</h4>
          <div className="chart-wrapper">
            {chart.type === 'bar' && <SimpleBar chart={chart} />}
            {chart.type === 'pie' && <SimplePie chart={chart} />}
            {chart.type === 'grouped_bar' && <GroupedBar chart={chart} />}
          </div>
        </div>
      ))}
    </div>
  );
}

function SimpleBar({ chart }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chart.data} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="name" tick={{ fill: '#a0a0b8', fontSize: 12 }} />
        <YAxis tick={{ fill: '#a0a0b8', fontSize: 11 }} tickFormatter={formatNum} />
        <Tooltip
          cursor={false}
          contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#e8e8f0' }}
          formatter={formatTooltip}
        />
        <Bar dataKey={chart.dataKey} fill={chart.color || '#6c63ff'} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function GroupedBar({ chart }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chart.data} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey="name" tick={{ fill: '#a0a0b8', fontSize: 12 }} />
        <YAxis tick={{ fill: '#a0a0b8', fontSize: 11 }} tickFormatter={formatNum} />
        <Tooltip
          cursor={false}
          contentStyle={{ background: '#1a1a2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#e8e8f0' }}
          formatter={formatTooltip}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: '#a0a0b8' }} />
        {chart.keys.map((key, i) => (
          <Bar key={key} dataKey={key} fill={chart.colors[i] || COLORS[i]} radius={[4, 4, 0, 0]} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

function SimplePie({ chart }) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={chart.data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={80}
          dataKey="value"
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          labelLine={{ stroke: '#a0a0b8' }}
        >
          {chart.data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}

function formatNum(val) {
  if (val >= 1000000) return `$${(val / 1000000).toFixed(1)}M`;
  if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
  return val;
}

function formatTooltip(value) {
  if (typeof value === 'number') {
    return value >= 100 ? value.toLocaleString() : value;
  }
  return value;
}

export default ChartPanel;
