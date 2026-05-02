import { useState } from "react";

const initialForm = {
  email: "",
  password: "",
  fullName: "",
};

export default function AuthPanel({ currentUser, onLogin, onRegister, onLogout }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      if (mode === "login") {
        await onLogin({ email: form.email, password: form.password });
      } else {
        await onRegister({
          email: form.email,
          password: form.password,
          full_name: form.fullName,
        });
        setMode("login");
      }
      setForm(initialForm);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (currentUser) {
    return (
      <div className="auth-shell">
        <div>
          <div className="auth-label">Authenticated session</div>
          <h2>{currentUser.full_name || currentUser.email}</h2>
          <p className="meta">
            {currentUser.email} · role: <strong>{currentUser.role}</strong>
          </p>
        </div>
        <button className="ghost" type="button" onClick={onLogout}>
          Sign out
        </button>
      </div>
    );
  }

  return (
    <div className="auth-shell auth-shell-stacked">
      <div className="auth-copy">
        <div className="auth-label">RBAC + JWT</div>
        <h2>Sign in to use the admin workflow</h2>
        <p className="meta">
          Accounts are stored in MySQL. Register creates a user account; admin
          access is granted by seeding or updating a role from the backend.
        </p>
      </div>

      <div className="auth-tabs">
        <button
          className={mode === "login" ? "auth-tab active" : "auth-tab"}
          type="button"
          onClick={() => setMode("login")}
        >
          Login
        </button>
        <button
          className={mode === "register" ? "auth-tab active" : "auth-tab"}
          type="button"
          onClick={() => setMode("register")}
        >
          Register
        </button>
      </div>

      <form className="auth-form" onSubmit={handleSubmit}>
        {mode === "register" && (
          <label className="field">
            <span>Full name</span>
            <input name="fullName" value={form.fullName} onChange={handleChange} />
          </label>
        )}

        <label className="field">
          <span>Email</span>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Working..." : mode === "login" ? "Sign in" : "Create account"}
        </button>
      </form>
    </div>
  );
}