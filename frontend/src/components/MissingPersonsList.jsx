export default function MissingPersonsList({ persons }) {
  return (
    <section>
      <h2>Missing Persons List</h2>
      {persons.length === 0 ? (
        <p className="meta">No missing person records yet.</p>
      ) : (
        <div className="card-list">
          {persons.map((person) => (
            <article className="card" key={person.id}>
              <h3>{person.name}</h3>
              <p className="meta">Last known city: {person.last_known_city}</p>
              <p className="meta">Height: {person.height_cm || "N/A"} cm</p>
              <p className="meta">Features: {person.physical_features?.join(", ") || "N/A"}</p>
              <p className="meta">Images: {person.image_paths?.length || 0}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
