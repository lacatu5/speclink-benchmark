import { useAuth } from "./hooks/useAuth";
import { LoginForm } from "./components/LoginForm";
import { Dashboard } from "./components/Dashboard";

function App() {
  const { user, login, register, logout } = useAuth();

  if (!user) {
    return <LoginForm onLogin={login} onRegister={register} />;
  }

  return <Dashboard onLogout={logout} />;
}

export default App;
