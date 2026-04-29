import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function PredictionChart({ title, data, lines }) {
  if (!data?.length) {
    return <div className="empty-state">{title} için çizilecek veri yok.</div>;
  }

  return (
    <section className="card">
      <div className="split" style={{ marginBottom: 12 }}>
        <div>
          <h3 className="panel-title">{title}</h3>
          <p className="helper-text">Gerçek veri ve tahmin akışı aynı görünümde izlenir.</p>
        </div>
      </div>
      <div className="chart-shell">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="rgba(148,163,184,0.12)" strokeDasharray="3 3" />
            <XAxis dataKey="label" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                background: "#081222",
                border: "1px solid rgba(148,163,184,0.18)",
                borderRadius: 14,
              }}
            />
            <Legend />
            {lines.map((line) => (
              <Line
                key={line.dataKey}
                type="monotone"
                dataKey={line.dataKey}
                name={line.name}
                stroke={line.stroke}
                strokeWidth={line.strokeWidth ?? 2.5}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
