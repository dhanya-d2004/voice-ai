import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = () => {
    navigate("/chat");
  };

  return (
    <div style={{ marginTop: "100px", textAlign: "center" }}>
      <h2>Login</h2>

      <div>
        <input
          type="email"
          placeholder="Enter Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ display: "block", margin: "10px auto", padding: "8px", width: "250px" }}
        />
      </div>

      <div>
        <input
          type="password"
          placeholder="Enter Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ display: "block", margin: "10px auto", padding: "8px", width: "250px" }}
        />
      </div>

      <button
        onClick={handleLogin}
        style={{ marginTop: "10px", padding: "8px 20px" }}
      >
        Login
      </button>

      <p style={{ marginTop: "15px" }}>
        Don’t have account? <Link to="/signup">Signup</Link>
      </p>
    </div>
  );
}

export default Login;
