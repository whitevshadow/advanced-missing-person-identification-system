import { useState } from "react";

const initialForm = {
  name: "",
  heightCm: "",
  physicalFeatures: "",
  lastKnownCity: "",
  reporterEmail: "",
  images: [],
};

export default function MissingPersonForm({ onSubmit }) {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleImageChange = (event) => {
    const selectedFiles = Array.from(event.target.files || []);
    setForm((prev) => ({ ...prev, images: selectedFiles }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!form.images.length) {
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
      <h2>Missing Person Registration</h2>
      <form onSubmit={handleSubmit}>
        <label className="field">
          <span>Name</span>
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="Full name"
            required
          />
        </label>

        <label className="field">
          <span>Height (cm)</span>
          <input
            name="heightCm"
            type="number"
            value={form.heightCm}
            onChange={handleChange}
            placeholder="e.g. 172"
          />
        </label>

        <label className="field">
          <span>Physical features (comma separated)</span>
          <input
            name="physicalFeatures"
            value={form.physicalFeatures}
            onChange={handleChange}
            placeholder="scar on left cheek, mole under eye"
          />
        </label>

        <label className="field">
          <span>Last known location (city)</span>
          <input
            name="lastKnownCity"
            value={form.lastKnownCity}
            onChange={handleChange}
            placeholder="City"
            required
          />
        </label>

        <label className="field">
          <span>Email for alerts</span>
          <input
            name="reporterEmail"
            type="email"
            value={form.reporterEmail}
            onChange={handleChange}
            placeholder="email@example.com"
            required
          />
        </label>

        <label className="field">
          <span>Upload one or more images</span>
          <input type="file" accept="image/*" multiple onChange={handleImageChange} required />
        </label>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : "Register Missing Person"}
        </button>
      </form>
    </section>
  );
}
