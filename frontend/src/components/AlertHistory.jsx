export default function AlertHistory({ alerts }) {
  return (
    <section>
      <h2>Alert History</h2>
      {alerts.length === 0 ? (
        <p className="meta">No alerts generated yet.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Status</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert) => (
              <tr key={alert.id}>
                <td>{alert.to_email}</td>
                <td>{alert.delivery_status}</td>
                <td>{alert.delivery_reason || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
