import { useNavigate } from "react-router-dom";
import { useState } from "react";
import styles from "./Home.module.css";

function Home() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    navigate("/chat", { state: { userMessage: query } });
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <img src="/logo.png" alt="logo" className={styles.logo} />
      </header>

      <main className={styles.main}>
        <h2>“궁금한 건강 정보, 지금 바로 물어보세요”</h2>
        <p>최신 의학 연구와 가이드를 기반으로 알려드립니다.</p>

        <form onSubmit={handleSearch} className={styles.searchBox}>
          <input
            placeholder="예: 기침이 2주 이상 지속될 때..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit">
            <img src="/search.png" alt="search" />
          </button>
        </form>
      </main>

      <img src="/hand.png" alt="hand" className={styles.hand} />
    </div>
  );
}

export default Home;
