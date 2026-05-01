import { useState } from "react";

const initialForm = {
  observedFeatures: "",
  currentCity: "",
  description: "",
  image: null,
};

export default function SightingForm({ onSubmit }) {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (event) => {
    const selected = event.target.files?.[0] || null;
    setForm((prev) => ({ ...prev, image: selected }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.image) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(form);
      setForm(initialForm);
      event.target.reset();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section>
      <h2>Sighting Report</h2>
      <form onSubmit={handleSubmit}>
        <label className="field">
          <span>Observed physical features</span>
          <input
            name="observedFeatures"
            value={form.observedFeatures}
            onChange={handleChange}
            placeholder="beard, right eyebrow scar"
          />
        </label>

        <label className="field">
          <span>Current location (city)</span>
          <input
            name="currentCity"
            value={form.currentCity}
            onChange={handleChange}
            placeholder="City"
            required
          />
        </label>

        <label className="field">
          <span>Description</span>
          <textarea
            name="description"
            value={form.description}
            onChange={handleChange}
            placeholder="Context about where/when the person was seen"
          />
        </label>

        <label className="field">
          <span>Upload suspected image</span>
          <input type="file" accept="image/*" onChange={handleImageChange} required />
        </label>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Processing..." : "Submit Sighting"}
        </button>
      </form>
    </section>
  );
}
