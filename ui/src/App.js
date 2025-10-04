import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PersonaSelect from "./pages/PersonaSelect";
import Home from "./pages/Home";
import Chat from "./pages/Chat";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<PersonaSelect />} />
        <Route path="/home" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </Router>
  );
}

export default App;
